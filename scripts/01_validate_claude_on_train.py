"""
Script 01: Validate Claude Haiku 3.5 on professor's manually labeled training data.

- Loads train.dta (1,000 rows, binary label: individual=0/1)
- Sends each entity name+country to Claude Haiku 3.5
- Compares Claude's prediction to the manual label
- Prints precision / recall / F1 and a confusion matrix

Cost: ~$0.05 | Runtime: ~3 minutes
Output: output/01_validation_results.csv, output/01_validation_report.txt
"""

import os
import sys
import json
import time
import pandas as pd
import anthropic
from sklearn.metrics import (
    classification_report, confusion_matrix, precision_score, recall_score, f1_score
)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
TRAIN_PATH = "/Users/puneeth/Documents/Research/Files/train.dta"
OUTPUT_CSV  = "/Users/puneeth/Documents/Research/Research_Claude/output/01_validation_results.csv"
OUTPUT_TXT  = "/Users/puneeth/Documents/Research/Research_Claude/output/01_validation_report.txt"
MODEL       = "claude-haiku-4-5-20251001"   # cheapest & fast; change to claude-sonnet-4-6 for max accuracy
BATCH_SIZE  = 50                            # calls per burst (avoids rate limit)
SLEEP_S     = 1.0                           # seconds between bursts

# ---------------------------------------------------------------------------
# FEW-SHOT PROMPT  (8 canonical examples covering all 4 classes + edge cases)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert entity classifier for a corporate ownership research database.

Given a company/person name and a 2-letter country code, classify the entity into EXACTLY ONE of:
  - individual      : a natural person (e.g. "JOHN SMITH", "AHMED AL RASHIDI", "ZHANG WEI")
  - company         : a corporation or business entity (e.g. "MIDWEST CARGO INC", "SCINTIA GMBH")
  - family_firm     : a business explicitly run by or named after a family (e.g. "SMITH & SONS LTD", "FAMILIA GARCIA SA")
  - government      : a state/government body (e.g. "MINISTRY OF FINANCE", "CITY OF CHICAGO")

Rules:
1. Prioritise PRECISION over recall — if genuinely ambiguous, output "unknown".
2. Legal entity suffixes (Ltd, GmbH, SA, Inc, LLC, SRL, AG, Sdn Bhd, Pty, SpA, AS, NV, BV …)
   strongly indicate company or family_firm.
3. Personal titles (MR, MRS, DR, SHEIKH, DATO, TAN SRI, SIR) indicate individual.
4. "& SONS", "& BROTHERS", "HERMANOS", "E FIGLI", "ET FILS", "FAMILY" indicate family_firm.
5. "MINISTRY", "DEPARTMENT", "GOVERNMENT", "AUTHORITY", "AGENCY", "MUNICIPAL",
   "BANCO CENTRAL", "RESERVE BANK" indicate government.

Return ONLY valid JSON with no extra text:
{"category": "<one of the four categories or unknown>", "confidence": <float 0.0-1.0>}

Examples:
Name: JOHN SMITH, Country: US  →  {"category": "individual", "confidence": 0.97}
Name: SCINTIA VERMÖGENSVERWALTUNGS GMBH, Country: AT  →  {"category": "company", "confidence": 0.99}
Name: SMITH & SONS LTD, Country: GB  →  {"category": "family_firm", "confidence": 0.95}
Name: MINISTRY OF FINANCE, Country: KE  →  {"category": "government", "confidence": 0.99}
Name: AHMED BIN RASHID AL MAKTOUM, Country: AE  →  {"category": "individual", "confidence": 0.93}
Name: GARCIA HERMANOS SL, Country: ES  →  {"category": "family_firm", "confidence": 0.94}
Name: CIUDAD DE BUENOS AIRES, Country: AR  →  {"category": "government", "confidence": 0.91}
Name: XYZ TRADING, Country: SG  →  {"category": "company", "confidence": 0.82}
"""


def classify_entity(client: anthropic.Anthropic, name: str, country: str) -> dict:
    """Call Claude for a single entity. Returns dict with category and confidence."""
    user_msg = f"Name: {name}, Country: {country}"
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=64,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        # Claude occasionally wraps in markdown fences — strip them
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return {
            "category":   result.get("category", "unknown"),
            "confidence": float(result.get("confidence", 0.0)),
            "raw":        raw,
        }
    except Exception as e:
        return {"category": "unknown", "confidence": 0.0, "raw": str(e)}


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY environment variable not set.\n"
                 "Run: export ANTHROPIC_API_KEY='sk-ant-...'")

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Loading training data from {TRAIN_PATH} ...")
    df = pd.read_stata(TRAIN_PATH)
    print(f"  Rows: {len(df)}, Columns: {df.columns.tolist()}")
    print(f"  Label distribution:\n{df['individual'].value_counts()}\n")

    # Build ground-truth binary: 1 = individual, 0 = not individual
    df["true_individual"] = df["individual"].astype(int)

    results = []
    total = len(df)

    print(f"Classifying {total} entities with {MODEL} ...")
    for i, row in df.iterrows():
        name    = str(row["Parent_name"]) if pd.notna(row["Parent_name"]) else ""
        country = str(row["parent_cty"])  if pd.notna(row["parent_cty"])  else ""
        res = classify_entity(client, name, country)
        pred_individual = 1 if res["category"] == "individual" else 0
        results.append({
            "Parent_name":     name,
            "parent_cty":      country,
            "true_individual": row["true_individual"],
            "pred_category":   res["category"],
            "pred_individual": pred_individual,
            "confidence":      res["confidence"],
        })

        # Progress + rate-limit courtesy sleep
        idx = list(df.index).index(i) + 1
        if idx % BATCH_SIZE == 0:
            pct = 100 * idx / total
            print(f"  [{idx}/{total}] {pct:.0f}% done ...")
            time.sleep(SLEEP_S)

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nResults saved → {OUTPUT_CSV}")

    # -----------------------------------------------------------------------
    # EVALUATION  (binary: individual vs not-individual)
    # -----------------------------------------------------------------------
    y_true = results_df["true_individual"]
    y_pred = results_df["pred_individual"]

    prec  = precision_score(y_true, y_pred, zero_division=0)
    rec   = recall_score(y_true, y_pred, zero_division=0)
    f1    = f1_score(y_true, y_pred, zero_division=0)
    cm    = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred,
                                   target_names=["not-individual", "individual"],
                                   zero_division=0)

    # Distribution of 4-class predictions
    cat_dist = results_df["pred_category"].value_counts()
    # Coverage (how many are not "unknown")
    n_unknown  = (results_df["pred_category"] == "unknown").sum()
    coverage   = 100 * (1 - n_unknown / total)

    report_lines = [
        "=" * 60,
        "ENTITY CLASSIFIER — VALIDATION REPORT",
        f"Model : {MODEL}",
        f"Data  : {TRAIN_PATH}",
        f"Total : {total} entities",
        "=" * 60,
        "",
        "BINARY EVALUATION (individual vs not-individual)",
        "-" * 40,
        f"Precision : {prec:.4f}",
        f"Recall    : {rec:.4f}",
        f"F1 Score  : {f1:.4f}",
        "",
        "Confusion Matrix (rows=true, cols=pred):",
        "            not-indiv  indiv",
        f"not-indiv   {cm[0][0]:9d}  {cm[0][1]:5d}",
        f"indiv       {cm[1][0]:9d}  {cm[1][1]:5d}",
        "",
        "Full Classification Report:",
        report,
        "",
        "4-CLASS PREDICTION DISTRIBUTION",
        "-" * 40,
        cat_dist.to_string(),
        "",
        f"Coverage (non-unknown): {coverage:.1f}%",
        f"Unknown count         : {n_unknown}",
        "=" * 60,
    ]

    report_text = "\n".join(report_lines)
    print("\n" + report_text)

    with open(OUTPUT_TXT, "w") as f:
        f.write(report_text)
    print(f"\nReport saved → {OUTPUT_TXT}")


if __name__ == "__main__":
    main()
