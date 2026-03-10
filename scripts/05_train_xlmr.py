"""
Script 05: Fine-tune XLM-RoBERTa for entity classification.

This is the core ML model — a multilingual transformer fine-tuned for high-precision,
low-recall entity classification across 120+ countries.

Architecture:
  - Base model : xlm-roberta-base (278M params, trained on 100 languages by Meta/Facebook)
  - Input      : "[entity name] </s> [country code]"
  - Output     : softmax over 4 classes (individual / company / family_firm / government)
  - Threshold  : Only classify if max softmax prob > CONFIDENCE_THRESHOLD
                 else → "unknown"  (this enforces high precision / low recall)

Training data:
  - Combines train.dta (professor's binary labels, used for individual detection)
  - + Claude API output from Script 04 (4-class labels, confidence-filtered)

Run on Google Colab (free T4 GPU) or NYU HPC for speed.
Local CPU is fine for small datasets but will be slow.

Usage:
  python3 05_train_xlmr.py --train_csv output/CLASSIFIED_ALL_PARENTS_FINAL.csv \
                            --train_dta /Users/puneeth/Documents/Research/Files/train.dta \
                            --output_dir output/xlmr_model

After training, use the model for inference:
  python3 05_train_xlmr.py --infer --model_dir output/xlmr_model \
                            --input_csv output/02_remaining_for_api.csv
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, precision_score, recall_score, f1_score,
    confusion_matrix,
)
from sklearn.utils.class_weight import compute_class_weight

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
MODEL_NAME           = "xlm-roberta-base"        # free on HuggingFace
LABELS               = ["individual", "company", "family_firm", "government"]
LABEL2ID             = {l: i for i, l in enumerate(LABELS)}
ID2LABEL             = {i: l for i, l in enumerate(LABELS)}
MAX_LEN              = 64        # entity names are short; 64 tokens is plenty
BATCH_SIZE           = 32
EPOCHS               = 10
LR                   = 2e-5
WARMUP_RATIO         = 0.1
WEIGHT_DECAY         = 0.01
CONFIDENCE_THRESHOLD = 0.80      # below this → "unknown"  (high precision design)
SEED                 = 42

torch.manual_seed(SEED)
np.random.seed(SEED)


# ---------------------------------------------------------------------------
# DATASET
# ---------------------------------------------------------------------------
class EntityDataset(Dataset):
    def __init__(self, names, countries, labels, tokenizer):
        self.encodings = tokenizer(
            [f"{n} {c}" for n, c in zip(names, countries)],
            max_length=MAX_LEN,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids":      self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels":         self.labels[idx],
        }


# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------
def load_training_data(claude_csv: str, train_dta: str,
                       min_confidence: float = 0.85) -> pd.DataFrame:
    """
    Combines two data sources:
      1. Claude API output (Script 04) — 4-class labels, filter by confidence
      2. train.dta — professor's binary labels (individual vs not)
         Only the "individual" rows are used here (high-quality confirmed individuals)
    """
    frames = []

    # Source 1: Claude API classifications (high-confidence only)
    if claude_csv and Path(claude_csv).exists():
        df_claude = pd.read_csv(claude_csv)
        # Keep only high-confidence, non-unknown predictions
        mask = (df_claude["confidence"] >= min_confidence) & \
               (df_claude["category"].isin(LABELS))
        df_claude = df_claude[mask][["Parent_name", "parent_cty", "category"]].copy()
        df_claude.rename(columns={"category": "label"}, inplace=True)
        frames.append(df_claude)
        print(f"  Claude source  : {len(df_claude):>8,} rows (conf ≥ {min_confidence})")

    # Source 2: Professor's manually coded data (train.dta)
    if train_dta and Path(train_dta).exists():
        df_train = pd.read_stata(train_dta)
        # Use "individual" column: 1 = individual, 0 = not individual
        # Map 1 → "individual"; map 0 → "company" (majority class in non-individual)
        # These are the cleanest labels we have from human annotation
        df_train = df_train[pd.notna(df_train["Parent_name"])].copy()
        df_train["label"] = df_train["individual"].apply(
            lambda x: "individual" if int(x) == 1 else "company"
        )
        df_train = df_train[["Parent_name", "parent_cty", "label"]].copy()
        frames.append(df_train)
        print(f"  Professor data : {len(df_train):>8,} rows (binary)")

    if not frames:
        sys.exit("ERROR: No training data found. Check file paths.")

    df = pd.concat(frames, ignore_index=True)
    df.dropna(subset=["Parent_name", "label"], inplace=True)
    df["Parent_name"] = df["Parent_name"].astype(str).str.strip()
    df["parent_cty"]  = df["parent_cty"].fillna("").astype(str).str.strip()

    # Deduplicate (same name+country pair, keep first label)
    df.drop_duplicates(subset=["Parent_name", "parent_cty"], keep="first", inplace=True)

    print(f"\n  Total training  : {len(df):,}")
    print(f"  Label distribution:\n{df['label'].value_counts().to_string()}\n")
    return df


# ---------------------------------------------------------------------------
# TRAINING
# ---------------------------------------------------------------------------
def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Model : {MODEL_NAME}\n")

    # Load data
    print("Loading training data ...")
    df = load_training_data(args.train_csv, args.train_dta,
                             min_confidence=args.min_confidence)

    # Encode labels
    df = df[df["label"].isin(LABELS)].copy()
    df["label_id"] = df["label"].map(LABEL2ID)

    # Stratified train/val split
    train_df, val_df = train_test_split(
        df, test_size=0.15, stratify=df["label_id"], random_state=SEED
    )
    print(f"Train: {len(train_df):,}  |  Val: {len(val_df):,}")

    # Tokenizer
    print(f"\nLoading tokenizer & model ({MODEL_NAME}) ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Datasets
    train_ds = EntityDataset(
        train_df["Parent_name"].tolist(), train_df["parent_cty"].tolist(),
        train_df["label_id"].tolist(), tokenizer
    )
    val_ds = EntityDataset(
        val_df["Parent_name"].tolist(), val_df["parent_cty"].tolist(),
        val_df["label_id"].tolist(), tokenizer
    )

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)

    # Class weights (handles imbalance — important for family_firm & government)
    class_weights = compute_class_weight(
        "balanced",
        classes=np.array(list(range(len(LABELS)))),
        y=train_df["label_id"].values,
    )
    weights_tensor = torch.tensor(class_weights, dtype=torch.float).to(device)
    print(f"Class weights: { {l: round(w, 2) for l, w in zip(LABELS, class_weights)} }\n")

    # Model
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    ).to(device)

    # Optimizer + scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    total_steps = len(train_loader) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )

    loss_fn = nn.CrossEntropyLoss(weight=weights_tensor)

    # Training loop
    best_val_f1   = 0.0
    best_val_prec = 0.0
    output_dir    = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    history       = []

    print("=" * 55)
    print("TRAINING")
    print("=" * 55)

    for epoch in range(1, EPOCHS + 1):
        # --- TRAIN ---
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attn_mask = batch["attention_mask"].to(device)
            labels    = batch["labels"].to(device)
            logits    = model(input_ids=input_ids, attention_mask=attn_mask).logits
            loss      = loss_fn(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            train_loss += loss.item()
        avg_train_loss = train_loss / len(train_loader)

        # --- VALIDATE ---
        model.eval()
        all_preds, all_true = [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attn_mask = batch["attention_mask"].to(device)
                labels    = batch["labels"].to(device)
                logits    = model(input_ids=input_ids, attention_mask=attn_mask).logits
                probs     = torch.softmax(logits, dim=-1)
                preds     = torch.argmax(probs, dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_true.extend(labels.cpu().numpy())

        # Metrics on ALL val predictions (no threshold — so we can see raw model accuracy)
        macro_prec = precision_score(all_true, all_preds, average="macro", zero_division=0)
        macro_rec  = recall_score(all_true,    all_preds, average="macro", zero_division=0)
        macro_f1   = f1_score(all_true,        all_preds, average="macro", zero_division=0)

        print(f"Epoch {epoch:>2}/{EPOCHS}  "
              f"train_loss={avg_train_loss:.4f}  "
              f"val_prec={macro_prec:.4f}  "
              f"val_rec={macro_rec:.4f}  "
              f"val_f1={macro_f1:.4f}")

        history.append({
            "epoch": epoch, "train_loss": avg_train_loss,
            "val_precision": macro_prec, "val_recall": macro_rec, "val_f1": macro_f1,
        })

        # Save best model (optimise for precision since requirement is high precision)
        if macro_prec > best_val_prec:
            best_val_prec = macro_prec
            best_val_f1   = macro_f1
            model.save_pretrained(output_dir / "best_model")
            tokenizer.save_pretrained(output_dir / "best_model")
            print(f"          ★ New best precision {macro_prec:.4f} — model saved")

    # Save training history
    with open(output_dir / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    # Final evaluation with threshold applied (HIGH PRECISION / LOW RECALL design)
    print("\n" + "=" * 55)
    print(f"FINAL EVALUATION  (threshold = {CONFIDENCE_THRESHOLD})")
    print("=" * 55)

    model.eval()
    all_probs, all_true_final = [], []
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            attn_mask = batch["attention_mask"].to(device)
            labels    = batch["labels"].to(device)
            logits    = model(input_ids=input_ids, attention_mask=attn_mask).logits
            probs     = torch.softmax(logits, dim=-1)
            all_probs.extend(probs.cpu().numpy())
            all_true_final.extend(labels.cpu().numpy())

    all_probs_arr = np.array(all_probs)
    max_probs     = all_probs_arr.max(axis=1)
    preds_thresh  = all_probs_arr.argmax(axis=1)

    # Apply threshold: low-confidence → label as "unknown" (-1)
    preds_thresh[max_probs < CONFIDENCE_THRESHOLD] = -1

    true_arr = np.array(all_true_final)

    # Only evaluate on predicted rows (not abstained)
    mask_predicted = preds_thresh >= 0
    n_abstained    = (~mask_predicted).sum()
    n_evaluated    = mask_predicted.sum()
    coverage       = 100 * n_evaluated / len(true_arr)

    if n_evaluated > 0:
        p_thresh = precision_score(true_arr[mask_predicted], preds_thresh[mask_predicted],
                                   average="macro", zero_division=0)
        r_thresh = recall_score(true_arr[mask_predicted], preds_thresh[mask_predicted],
                                average="macro", zero_division=0)
        f_thresh = f1_score(true_arr[mask_predicted], preds_thresh[mask_predicted],
                            average="macro", zero_division=0)
        report   = classification_report(
            true_arr[mask_predicted], preds_thresh[mask_predicted],
            target_names=LABELS, zero_division=0
        )
    else:
        p_thresh = r_thresh = f_thresh = 0.0
        report   = "No predictions above threshold."

    eval_summary = "\n".join([
        f"Confidence threshold : {CONFIDENCE_THRESHOLD}",
        f"Abstained (unknown)  : {n_abstained:,}  ({100-coverage:.1f}%)",
        f"Evaluated            : {n_evaluated:,}  ({coverage:.1f}%)",
        f"Macro Precision      : {p_thresh:.4f}   ← this is the key metric",
        f"Macro Recall         : {r_thresh:.4f}",
        f"Macro F1             : {f_thresh:.4f}",
        "",
        "Per-class report (on predicted rows only):",
        report,
    ])
    print(eval_summary)

    with open(output_dir / "eval_report.txt", "w") as f:
        f.write(eval_summary)

    # Save model config with threshold
    cfg = {
        "base_model": MODEL_NAME, "labels": LABELS,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "max_len": MAX_LEN, "trained_at": datetime.utcnow().isoformat() + "Z",
        "best_val_precision": best_val_prec, "best_val_f1": best_val_f1,
    }
    with open(output_dir / "model_config.json", "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"\nModel saved → {output_dir / 'best_model'}")
    print(f"Config saved → {output_dir / 'model_config.json'}")
    print(f"Eval report  → {output_dir / 'eval_report.txt'}")


# ---------------------------------------------------------------------------
# INFERENCE  (apply trained model to new data)
# ---------------------------------------------------------------------------
def infer(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_dir = Path(args.model_dir) / "best_model"

    print(f"Loading model from {model_dir} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model     = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    model.eval()

    # Load config (threshold)
    cfg_path = Path(args.model_dir) / "model_config.json"
    threshold = CONFIDENCE_THRESHOLD
    if cfg_path.exists():
        with open(cfg_path) as f:
            cfg = json.load(f)
        threshold = cfg.get("confidence_threshold", CONFIDENCE_THRESHOLD)
        labels    = cfg.get("labels", LABELS)
    else:
        labels = LABELS
    print(f"Confidence threshold: {threshold}")

    # Load input
    df = pd.read_csv(args.input_csv)
    names    = df["Parent_name"].fillna("").astype(str).tolist()
    countries = df["parent_cty"].fillna("").astype(str).tolist()

    results = []
    for i in range(0, len(names), BATCH_SIZE):
        batch_names    = names[i:i+BATCH_SIZE]
        batch_countries = countries[i:i+BATCH_SIZE]
        enc = tokenizer(
            [f"{n} {c}" for n, c in zip(batch_names, batch_countries)],
            max_length=MAX_LEN, padding="max_length",
            truncation=True, return_tensors="pt",
        )
        with torch.no_grad():
            logits = model(
                input_ids      = enc["input_ids"].to(device),
                attention_mask = enc["attention_mask"].to(device),
            ).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        for j in range(len(batch_names)):
            max_prob = probs[j].max()
            pred_id  = probs[j].argmax()
            category = labels[pred_id] if max_prob >= threshold else "unknown"
            results.append({
                "category":   category,
                "confidence": float(max_prob),
                "method":     "xlmr" if category != "unknown" else "unknown",
            })
        if (i // BATCH_SIZE) % 20 == 0:
            print(f"  Inferred {min(i+BATCH_SIZE, len(names)):,}/{len(names):,} ...")

    result_df = df.copy()
    result_df["category"]   = [r["category"] for r in results]
    result_df["confidence"] = [r["confidence"] for r in results]
    result_df["method"]     = [r["method"] for r in results]

    out_path = args.output_csv or args.input_csv.replace(".csv", "_xlmr_classified.csv")
    result_df.to_csv(out_path, index=False)
    print(f"\nClassified output saved → {out_path}")

    cat_dist = result_df["category"].value_counts()
    print(f"\nCategory distribution:\n{cat_dist.to_string()}")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XLM-RoBERTa Entity Classifier")
    parser.add_argument("--infer",       action="store_true",
                        help="Run inference instead of training")
    # Training args
    parser.add_argument("--train_csv",   default="output/CLASSIFIED_ALL_PARENTS_FINAL.csv",
                        help="Claude-classified CSV (Script 04 output)")
    parser.add_argument("--train_dta",   default="/Users/puneeth/Documents/Research/Files/train.dta",
                        help="Professor's manually labeled .dta file")
    parser.add_argument("--min_confidence", type=float, default=0.85,
                        help="Minimum confidence to include Claude labels in training")
    parser.add_argument("--output_dir",  default="output/xlmr_model",
                        help="Where to save the trained model and reports")
    # Inference args
    parser.add_argument("--model_dir",   default="output/xlmr_model",
                        help="Directory with saved model (for --infer mode)")
    parser.add_argument("--input_csv",   default="",
                        help="CSV to classify (for --infer mode)")
    parser.add_argument("--output_csv",  default="",
                        help="Output path (for --infer mode, optional)")

    args = parser.parse_args()

    if args.infer:
        if not args.input_csv:
            sys.exit("ERROR: --input_csv required for inference mode.")
        infer(args)
    else:
        train(args)
