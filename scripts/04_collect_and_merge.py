"""
Script 04: Collect Batch API results and merge into final classified dataset.

- Polls all batch IDs from output/03_batch_ids.json
- Downloads results for completed batches
- Parses Claude's JSON responses (category + confidence)
- Merges with rule-classified entities from Script 02
- Writes the final CLASSIFIED_ALL_PARENTS_FINAL.csv

Run this script repeatedly until all batches complete.
Results are typically ready within 1-4 hours of submission.

Output:
  output/04_claude_results.csv           — Claude API classifications only
  output/CLASSIFIED_ALL_PARENTS_FINAL.csv — merged final dataset (all 1.4M)
  output/04_final_summary.txt            — coverage & class distribution
"""

import os
import sys
import json
import time
import pandas as pd
import anthropic
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
RULE_CSV       = "/Users/puneeth/Documents/Research/Research_Claude/output/02_rule_classified.csv"
REMAINING_CSV  = "/Users/puneeth/Documents/Research/Research_Claude/output/02_remaining_for_api.csv"
BATCH_IDS_FILE = "/Users/puneeth/Documents/Research/Research_Claude/output/03_batch_ids.json"
CLAUDE_CSV     = "/Users/puneeth/Documents/Research/Research_Claude/output/04_claude_results.csv"
FINAL_CSV      = "/Users/puneeth/Documents/Research/Research_Claude/output/CLASSIFIED_ALL_PARENTS_FINAL.csv"
SUMMARY_TXT    = "/Users/puneeth/Documents/Research/Research_Claude/output/04_final_summary.txt"

CONFIDENCE_THRESHOLD = 0.80   # below this → mark as "unknown"
POLL_INTERVAL_S      = 30     # seconds between status polls


# ---------------------------------------------------------------------------
# COLLECT BATCH RESULTS
# ---------------------------------------------------------------------------

def fetch_all_results(client: anthropic.Anthropic, batch_log: list) -> dict:
    """
    Polls batches until all are complete.
    Returns dict: custom_id → {category, confidence}
    """
    pending = {b["batch_id"]: b for b in batch_log if b["status"] != "collected"}
    results = {}

    if not pending:
        print("All batches already marked as collected.")
        return results

    print(f"Waiting for {len(pending)} batch(es) to complete ...")

    while pending:
        still_pending = {}
        for batch_id, meta in pending.items():
            try:
                batch = client.messages.batches.retrieve(batch_id)
            except Exception as e:
                print(f"  ERROR retrieving {batch_id}: {e}")
                still_pending[batch_id] = meta
                continue

            status = batch.processing_status
            counts = batch.request_counts
            print(f"  {batch_id}  status={status}  "
                  f"succeeded={counts.succeeded}  errored={counts.errored}  "
                  f"processing={counts.processing}")

            if status == "ended":
                # Download results
                print(f"    → Downloading results for {batch_id} ...")
                for result in client.messages.batches.results(batch_id):
                    cid = result.custom_id
                    if result.result.type == "succeeded":
                        raw = result.result.message.content[0].text.strip()
                        raw = raw.replace("```json", "").replace("```", "").strip()
                        try:
                            parsed = json.loads(raw)
                            results[cid] = {
                                "category":   parsed.get("category", "unknown"),
                                "confidence": float(parsed.get("confidence", 0.0)),
                            }
                        except Exception:
                            results[cid] = {"category": "unknown", "confidence": 0.0}
                    else:
                        results[cid] = {"category": "unknown", "confidence": 0.0}

                # Mark as collected
                for b in batch_log:
                    if b["batch_id"] == batch_id:
                        b["status"] = "collected"
                        b["collected_at"] = datetime.utcnow().isoformat() + "Z"

                # Persist updated batch log
                with open(BATCH_IDS_FILE, "w") as f:
                    json.dump(batch_log, f, indent=2)

                print(f"    ✓ Collected {len([r for r in results])} results so far.")

            elif status in ("canceling", "expired"):
                print(f"    ✗ Batch {batch_id} {status}! Results unavailable.")
                for b in batch_log:
                    if b["batch_id"] == batch_id:
                        b["status"] = status
            else:
                still_pending[batch_id] = meta  # still in_progress

        pending = still_pending
        if pending:
            print(f"\n  {len(pending)} batch(es) still processing. "
                  f"Waiting {POLL_INTERVAL_S}s ...\n")
            time.sleep(POLL_INTERVAL_S)

    print(f"\nAll batches complete. Total Claude results: {len(results):,}\n")
    return results


# ---------------------------------------------------------------------------
# PARSE & APPLY CONFIDENCE THRESHOLD
# ---------------------------------------------------------------------------

def build_claude_df(remaining_df: pd.DataFrame, results: dict,
                    threshold: float) -> pd.DataFrame:
    """
    Reconstructs rows for the API-classified entities.
    Uses the same custom_id format as Script 03: f"{global_i}_{pid}"
    """
    rows = []
    for local_i, (_, row) in enumerate(remaining_df.iterrows()):
        name    = str(row.get("Parent_name", ""))
        pid     = str(row.get("parent_ID", local_i))
        country = str(row.get("parent_cty", ""))
        cid     = f"{local_i}_{pid}"

        res = results.get(cid, {"category": "unknown", "confidence": 0.0})
        cat = res["category"]
        conf = res["confidence"]

        # Apply threshold
        if cat != "unknown" and conf < threshold:
            cat  = "unknown"
            conf = conf  # keep original conf so analyst can review

        rows.append({
            "Parent_name": name,
            "parent_ID":   row.get("parent_ID", ""),
            "parent_cty":  country,
            "category":    cat,
            "confidence":  conf,
            "method":      "claude_api" if cat != "unknown" else "unknown",
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set.")

    client = anthropic.Anthropic(api_key=api_key)

    # Load batch IDs
    if not Path(BATCH_IDS_FILE).exists():
        sys.exit(f"ERROR: {BATCH_IDS_FILE} not found. Run script 03 first.")
    with open(BATCH_IDS_FILE) as f:
        batch_log = json.load(f)
    print(f"Found {len(batch_log)} batch(es) in log.\n")

    # Collect results (polls until done)
    results = fetch_all_results(client, batch_log)

    # Load remaining CSV (to reconstruct full rows)
    remaining_df = pd.read_csv(REMAINING_CSV)
    print(f"Remaining entities (sent to API): {len(remaining_df):,}")

    # Build Claude results dataframe
    claude_df = build_claude_df(remaining_df, results, CONFIDENCE_THRESHOLD)
    claude_df.to_csv(CLAUDE_CSV, index=False)
    print(f"Claude results saved → {CLAUDE_CSV}")

    # Load rule-classified entities
    rule_df = pd.read_csv(RULE_CSV)
    print(f"Rule-classified entities        : {len(rule_df):,}")

    # Merge everything
    final_df = pd.concat([rule_df, claude_df], ignore_index=True)
    final_df.to_csv(FINAL_CSV, index=False)
    print(f"\nFinal merged dataset saved → {FINAL_CSV}")

    # ---------------------------------------------------------------------------
    # SUMMARY REPORT
    # ---------------------------------------------------------------------------
    total      = len(final_df)
    cat_counts = final_df["category"].value_counts()
    method_cts = final_df["method"].value_counts()
    n_unknown  = (final_df["category"] == "unknown").sum()
    coverage   = 100 * (1 - n_unknown / total) if total else 0

    # Per-country breakdown (top 20)
    country_df = (
        final_df[final_df["category"] != "unknown"]
        .groupby(["parent_cty", "category"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    summary_lines = [
        "=" * 60,
        "FINAL CLASSIFICATION SUMMARY",
        f"Generated : {datetime.utcnow().isoformat()}Z",
        "=" * 60,
        "",
        f"Total entities   : {total:>10,}",
        f"Coverage (≠ unkn): {coverage:>9.1f}%",
        f"Unknown          : {n_unknown:>10,}",
        "",
        "BY CATEGORY",
        "-" * 40,
    ]
    for cat in ["company", "individual", "family_firm", "government", "unknown"]:
        n = cat_counts.get(cat, 0)
        pct = 100 * n / total if total else 0
        summary_lines.append(f"  {cat:<15}: {n:>8,}  ({pct:.1f}%)")

    summary_lines += [
        "",
        "BY METHOD",
        "-" * 40,
    ]
    for meth, n in method_cts.items():
        pct = 100 * n / total if total else 0
        summary_lines.append(f"  {meth:<15}: {n:>8,}  ({pct:.1f}%)")

    summary_lines += [
        "",
        "CONFIDENCE STATS (claude_api rows only)",
        "-" * 40,
    ]
    api_conf = claude_df[claude_df["method"] == "claude_api"]["confidence"]
    if len(api_conf):
        summary_lines += [
            f"  Mean   : {api_conf.mean():.3f}",
            f"  Median : {api_conf.median():.3f}",
            f"  Min    : {api_conf.min():.3f}",
            f"  Max    : {api_conf.max():.3f}",
        ]

    summary_lines += [
        "",
        f"Output file : {FINAL_CSV}",
        "=" * 60,
    ]

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)
    with open(SUMMARY_TXT, "w") as f:
        f.write(summary_text)
    print(f"\nSummary saved → {SUMMARY_TXT}")


if __name__ == "__main__":
    main()
