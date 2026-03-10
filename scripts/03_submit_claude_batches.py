"""
Script 03: Submit remaining entities to Anthropic Batches API overnight.

- Reads output/02_remaining_for_api.csv  (entities rule-based couldn't classify)
- Packages them as an Anthropic Message Batch (up to 100K requests per batch)
- Submits one batch per 10K rows (API limit: 100K; we use 10K for easy tracking)
- Saves batch IDs to output/03_batch_ids.json  — used by Script 04 to collect results

Cost: ~$12-16 for 512K entities (Claude Haiku 3 + short prompt + Batches 50% discount)
Runtime to SUBMIT: ~5 min | Results ready: 1-4 hours after submission
Output: output/03_batch_ids.json
"""

import os
import re
import sys
import json
import time
import math
import pandas as pd
import anthropic
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
REMAINING_CSV  = "/Users/puneeth/Documents/Research/Research_Claude/output/02_remaining_for_api.csv"
BATCH_IDS_FILE = "/Users/puneeth/Documents/Research/Research_Claude/output/03_batch_ids.json"
MODEL          = "claude-haiku-4-5-20251001"  # ← ONLY model confirmed working with Batches on this account
ROWS_PER_BATCH = 10_000          # API max is 100K; 10K keeps batches manageable
SLEEP_BETWEEN  = 2.0             # seconds between batch submissions (be polite)

# ---------------------------------------------------------------------------
# COMPACT SYSTEM PROMPT  (~120 tokens — keeps cost low for 512K requests)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Classify a business/person name + 2-letter country code into one of:
individual | company | family_firm | government | unknown

Rules (prefer precision over recall — use unknown if unsure):
- individual: natural person, personal titles (MR, DR, SHEIKH, BIN, DATO)
- company: legal suffixes (LTD, INC, GMBH, SA, LLC, SRL, AG, PTE, SDN BHD, SPA, NV, BV, AS...)
- family_firm: "& SONS", "HERMANOS", "FRATELLI", "ET FILS", "FAMILY", "BROTHERS"
- government: MINISTRY, DEPARTMENT, GOVERNMENT, AUTHORITY, AGENCY, MUNICIPAL, CENTRAL BANK

Reply ONLY with JSON: {"category": "...", "confidence": 0.0-1.0}"""


def make_request(custom_id: str, name: str, country: str) -> dict:
    """Format a single Batch API request object."""
    # custom_id must match ^[a-zA-Z0-9_-]{1,64}$
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", str(custom_id))[:64]
    return {
        "custom_id": safe_id,
        "params": {
            "model": MODEL,
            "max_tokens": 64,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": f"Name: {name}, Country: {country}"}
            ],
        },
    }


def submit_batch(client: anthropic.Anthropic, requests: list) -> str:
    """Submit a list of request dicts as one Batch job. Returns batch_id."""
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set.\nRun: export ANTHROPIC_API_KEY='sk-ant-...'")

    client = anthropic.Anthropic(api_key=api_key)

    if not Path(REMAINING_CSV).exists():
        sys.exit(f"ERROR: {REMAINING_CSV} not found.\nRun script 02 first.")

    df = pd.read_csv(REMAINING_CSV)
    total = len(df)
    print(f"Loaded {total:,} entities to send to Claude Batches API.")

    n_batches = math.ceil(total / ROWS_PER_BATCH)
    print(f"Will submit {n_batches} batch(es) of up to {ROWS_PER_BATCH:,} rows each.\n")

    # Load existing batch IDs if resuming a partial run
    if Path(BATCH_IDS_FILE).exists():
        with open(BATCH_IDS_FILE) as f:
            batch_log = json.load(f)
        print(f"Resuming — found {len(batch_log)} previously submitted batch(es).")
    else:
        batch_log = []

    already_submitted = {b["start_row"] for b in batch_log}

    for batch_num in range(n_batches):
        start = batch_num * ROWS_PER_BATCH
        end   = min(start + ROWS_PER_BATCH, total)

        if start in already_submitted:
            print(f"  Batch {batch_num+1}/{n_batches} (rows {start}-{end}) — already submitted, skipping.")
            continue

        chunk = df.iloc[start:end]
        requests = []
        for local_i, (_, row) in enumerate(chunk.iterrows()):
            global_i = start + local_i
            name    = str(row.get("Parent_name", ""))
            country = str(row.get("parent_cty", ""))
            pid     = str(row.get("parent_ID", global_i))
            cid     = f"{global_i}_{pid}"          # unique custom_id
            requests.append(make_request(cid, name, country))

        print(f"  Submitting batch {batch_num+1}/{n_batches}  "
              f"(rows {start:,}–{end:,}, {len(requests):,} requests) ...", end=" ", flush=True)

        try:
            batch_id = submit_batch(client, requests)
            print(f"OK  →  {batch_id}")
        except Exception as e:
            print(f"FAILED: {e}")
            print("Saving progress and stopping. Re-run script to resume.")
            break

        batch_log.append({
            "batch_id":   batch_id,
            "batch_num":  batch_num + 1,
            "start_row":  start,
            "end_row":    end,
            "n_requests": len(requests),
            "submitted_at": datetime.utcnow().isoformat() + "Z",
            "status":     "submitted",
        })

        # Persist after every batch so we can resume if interrupted
        with open(BATCH_IDS_FILE, "w") as f:
            json.dump(batch_log, f, indent=2)

        if batch_num < n_batches - 1:
            time.sleep(SLEEP_BETWEEN)

    # Final summary
    print("\n" + "=" * 55)
    print(f"Submitted {len(batch_log)} batch(es).")
    print(f"Batch IDs saved → {BATCH_IDS_FILE}")
    print("\nResults will be ready in ~1-4 hours.")
    print("Run script 04 to check status and collect results.")
    print("=" * 55)


if __name__ == "__main__":
    main()
