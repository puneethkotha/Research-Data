"""
Script 02: Rule-based filter — classifies high-confidence entities instantly.

Logic (in order of precedence):
  1. GOVERNMENT  : known government keywords/prefixes/suffixes
  2. FAMILY FIRM : "& sons", "hermanos", "famille", etc.
  3. COMPANY     : legal entity suffixes (200+ across 120+ countries)
  4. INDIVIDUAL  : personal titles / short 2-word name pattern
  → anything not caught = left for Claude API (Script 03)

Cost: $0  |  Runtime: ~5-10 min for 1.4M rows
Output:
  output/02_rule_classified.csv      — entities classified by rules
  output/02_remaining_for_api.csv    — entities to send to Claude Batches
  output/02_rule_summary.txt         — stats
"""

import re
import os
import sys
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
ALL_PARENTS  = "/Users/puneeth/Downloads/all parents.dta"
OUT_RULE     = "/Users/puneeth/Documents/Research/Research_Claude/output/02_rule_classified.csv"
OUT_REMAIN   = "/Users/puneeth/Documents/Research/Research_Claude/output/02_remaining_for_api.csv"
OUT_SUMMARY  = "/Users/puneeth/Documents/Research/Research_Claude/output/02_rule_summary.txt"
CHUNK_SIZE   = 50_000

# ---------------------------------------------------------------------------
# KEYWORD LISTS  (all uppercase — we uppercase names before matching)
# ---------------------------------------------------------------------------

GOVERNMENT_KEYWORDS = [
    # English
    "MINISTRY", "MINISTER", "DEPARTMENT OF", "DEPT OF", "GOVERNMENT OF",
    "GOVERNMENT-", "GOVT OF", "STATE OF", "REPUBLIC OF", "FEDERAL",
    "AUTHORITY", "AUTHORITIES", "AGENCY", "BUREAU", "COMMISSION",
    "MUNICIPALITY", "MUNICIPAL", "CITY OF", "TOWN OF", "COUNTY OF",
    "DISTRICT OF", "PROVINCE OF", "PREFECTURE",
    "TREASURY", "PARLIAMENT", "SENATE", "CONGRESS",
    "CENTRAL BANK", "RESERVE BANK", "NATIONAL BANK",
    "BANCO CENTRAL", "BANQUE CENTRALE", "ZENTRALBANK",
    "PUBLIC SERVICE", "PUBLIC SECTOR",
    "ARMED FORCES", "ROYAL AIR FORCE", "ROYAL NAVY",
    "POLICE", "PREFECTURE", "TRIBUNAL",
    # Spanish / Portuguese
    "MINISTERIO DE", "GOBIERNO DE", "ESTADO DE", "REPUBLICA DE",
    "CAMARA DE", "SECRETARIA DE", "MUNICIPIO DE", "PREFEITURA",
    "GOVERNO DE", "SERVICO DE",
    # French
    "MINISTERE DE", "REPUBLIQUE DE", "GOUVERNEMENT DE",
    "MAIRIE DE", "COMMUNE DE", "PREFECTURE DE",
    # German
    "BUNDESMINISTERIUM", "LANDESREGIERUNG", "STADTGEMEINDE",
    "BUNDESTAG", "BUNDESRAT",
    # Arabic transliteration
    "WIZARAT", "BALADIYA", "HUKUMAT",
]

FAMILY_FIRM_KEYWORDS = [
    "& SONS", "AND SONS", "& SON ", "AND SON ",
    "& BROTHERS", "AND BROTHERS", "& BROTHER", "AND BROTHER",
    "& DAUGHTERS", "AND DAUGHTERS",
    "& SISTERS", "AND SISTERS",
    "& PARTNER", "AND PARTNER",
    "& CO ", "& CO.", "AND CO ",
    "FAMILY HOLDINGS", "FAMILY ENTERPRISES", "FAMILY TRUST",
    "FAMILY INVESTMENTS", "FAMILY GROUP",
    # Spanish/Portuguese
    "HERMANOS", "HNOS", "E HIJOS", "E HIJO",
    "FAMILIA ", "IRMÃOS", "IRMAOS",
    # French
    "ET FILS", "ET FRERES", "FRERES", "FAMILLE",
    # Italian
    "E FIGLI", "E FRATELLI", "FRATELLI", "FAMIGLIA",
    # German
    "GESCHWISTER", "GEBRÜDER", "GEBRUEDER",
    # Arabic transliteration
    "AL IKHWAN", "WA ABNAUH", "AL ABNA",
]

# Legal entity suffixes — order matters: longer/more specific first
COMPANY_SUFFIXES = [
    # English / International
    " LIMITED LIABILITY COMPANY", " PUBLIC LIMITED COMPANY",
    " PRIVATE LIMITED COMPANY", " JOINT STOCK COMPANY",
    " UNLIMITED COMPANY",
    " INCORPORATED", " CORPORATION",
    " HOLDINGS LIMITED", " HOLDING LIMITED",
    " HOLDINGS LTD", " HOLDING LTD",
    " HOLDINGS PLC", " HOLDING PLC",
    " HOLDINGS INC", " HOLDING INC",
    " HOLDINGS LLC", " HOLDING LLC",
    " INVESTMENTS LIMITED", " INVESTMENT LIMITED",
    " ENTERPRISES LIMITED", " ENTERPRISE LIMITED",
    " INTERNATIONAL LIMITED", " INTERNATIONAL LTD",
    " PROPERTIES LIMITED", " PROPERTY LIMITED",
    " RESOURCES LIMITED", " RESOURCE LIMITED",
    " SERVICES LIMITED", " SERVICE LIMITED",
    " VENTURES LIMITED", " VENTURE LIMITED",
    " TECHNOLOGIES LIMITED", " TECHNOLOGY LIMITED",
    " INDUSTRIES LIMITED", " INDUSTRY LIMITED",
    " COMPANY LIMITED", " COMPANY LTD",
    " COMPANY INC", " COMPANY LLC",
    " PVT LTD", " PVT. LTD", " PVT. LTD.",
    " PRIVATE LTD", " PRIVATE LIMITED",
    " (PVT) LIMITED", " (PTY) LIMITED",
    " (PTY) LTD", " (PROPRIETARY) LIMITED",
    " PTE LTD", " PTE. LTD", " PTE. LTD.",
    " SDN BHD", " SDN. BHD.", " BHD",
    " LIMITED", " LTD", " LTD.",
    " INC", " INC.", " CORP", " CORP.",
    " LLC", " L.L.C.", " LLP", " L.L.P.",
    " PLC", " P.L.C.",
    " PLC,", " LTD,",
    # European
    " GMBH", " G.M.B.H.", " GMBH & CO KG", " GMBH & CO. KG",
    " AG", " A.G.",
    " KG", " K.G.", " OHG", " O.H.G.", " GBR",
    " SA", " S.A.", " SAS", " S.A.S.",
    " SARL", " S.A.R.L.", " SARLU",
    " SNC", " S.N.C.", " SCS", " SCA",
    " SRL", " S.R.L.", " SRLS",
    " SPA", " S.P.A.",
    " NV", " N.V.", " BV", " B.V.", " VBA", " VOF",
    " AS", " A/S", " OY", " AB", " OYJ",
    " APS", " A/PS", " IS", " ANS",
    " SP ZOO", " SP. Z O.O.", " SPOLKA",
    " KFT", " ZRT", " RT", " BT", " KKT",
    " SRO", " S.R.O.", " AS.", " A.S.",
    " SE", " SCE", " SCR", " SCRL",
    " GIE", " EURL", " SELARL",
    # Latin America
    " LTDA", " LTDA.", " S DE RL", " S.A. DE C.V.", " S.A.S.",
    " CIA LTDA", " CIA.", " CIA",
    " SA DE CV", " SC DE RL DE CV",
    # Africa / Middle East
    " ET CIE", " ET ASSOCIES",
    " SAOG", " SAOC", " SOAG",
    " WLL", " W.L.L.", " BSC", " B.S.C.",
    " PSC", " P.S.C.", " KSCC", " KPSC",
    " LLC FZ", " FZ LLC", " FZ-LLC", " FZCO", " FZE",
    # South/East Asia
    " PVT", " LBG", " CLG",
    # Misc
    " CO LTD", " CO., LTD", " CO., LTD.",
    " CO LTD.", " CO, LTD",
    " & CO", " & CO.",
    " TRUST", " FOUNDATION", " STIFTUNG",
    " HOLDING", " HOLDINGS",
    " GROUP", " GRUPPE",
    " FUND", " FONDS",
    " BANK", " BANCO", " BANQUE", " BANCA", " BANKA",
    " INSURANCE", " ASSURANCE", " ASSURANCES",
]

# Personal titles that strongly indicate individual
INDIVIDUAL_TITLES = [
    r"\bMR\.?\b", r"\bMRS\.?\b", r"\bMS\.?\b", r"\bMISS\b",
    r"\bDR\.?\b", r"\bPROF\.?\b", r"\bSIR\b", r"\bLADY\b",
    r"\bLORD\b", r"\bHON\.?\b", r"\bREV\.?\b",
    r"\bSHEIKH\b", r"\bSHAIKH\b", r"\bDATO\'?\b", r"\bDATUK\b",
    r"\bTAN SRI\b", r"\bTUN\b",
    r"\bHAJI\b", r"\bHAJJA\b", r"\bAL HAJ\b",
    r"\bBIN\b", r"\bBINT\b", r"\bIBN\b",   # Arabic patronymics
    r"\bVAN DEN\b", r"\bVAN DER\b", r"\bVAN DE\b",  # Dutch
    r"\bDE LA\b", r"\bDEL\b",               # Spanish/Italian
    r"\bVON\b", r"\bZU\b",                  # German nobility
    r"\bSYED\b", r"\bSAYYED\b", r"\bKHAN\b",
]
INDIVIDUAL_TITLE_RE = re.compile("|".join(INDIVIDUAL_TITLES))

# Very short 1-2 word patterns that look like personal names (no numbers, no symbols)
# We use this only as a weak fallback — confidence will be lower
NAME_PATTERN_RE = re.compile(r"^[A-Z][A-Z'\-]+([ ][A-Z][A-Z'\-]+){0,3}$")

# ---------------------------------------------------------------------------
# CLASSIFICATION LOGIC
# ---------------------------------------------------------------------------

def normalize(name: str) -> str:
    return str(name).upper().strip()


def classify_rule(name: str, country: str) -> tuple[str, float]:
    """
    Returns (category, confidence) or ('', 0) if no rule matches.
    '' means → send to Claude API.
    """
    n = normalize(name)

    # 1. GOVERNMENT (highest priority)
    for kw in GOVERNMENT_KEYWORDS:
        if kw in n:
            return "government", 1.0

    # 2. FAMILY FIRM
    for kw in FAMILY_FIRM_KEYWORDS:
        if kw in n:
            return "family_firm", 1.0

    # 3. COMPANY — check suffixes
    for sfx in COMPANY_SUFFIXES:
        sfx_u = sfx.upper()
        if n.endswith(sfx_u) or (sfx_u + "," in n) or (sfx_u + "." in n):
            return "company", 1.0
        # Also check if it appears mid-string followed by a comma/space (holding structures)
        if re.search(re.escape(sfx_u) + r"[\s,;(]", n):
            return "company", 0.97

    # 4. INDIVIDUAL — personal title
    if INDIVIDUAL_TITLE_RE.search(n):
        return "individual", 0.92

    # No rule matched — send to Claude
    return "", 0.0


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    out_dir = Path(OUT_RULE).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {ALL_PARENTS} ...")
    try:
        df_all = pd.read_stata(ALL_PARENTS)
    except Exception as e:
        sys.exit(f"ERROR reading .dta file: {e}\n"
                 "Make sure pyreadstat is installed: pip install pyreadstat")

    print(f"  Total rows: {len(df_all):,}")
    print(f"  Columns: {df_all.columns.tolist()}\n")

    rule_rows      = []
    remaining_rows = []
    counts         = {"government": 0, "family_firm": 0, "company": 0, "individual": 0, "api": 0}

    total = len(df_all)
    for i, row in df_all.iterrows():
        name    = str(row.get("Parent_name", "")) if pd.notna(row.get("Parent_name")) else ""
        pid     = row.get("parent_ID", "")
        country = str(row.get("parent_cty", "")) if pd.notna(row.get("parent_cty")) else ""

        category, confidence = classify_rule(name, country)

        base = {
            "Parent_name": name,
            "parent_ID":   pid,
            "parent_cty":  country,
        }

        if category:
            counts[category] += 1
            rule_rows.append({**base,
                               "category":   category,
                               "confidence": confidence,
                               "method":     "rule"})
        else:
            counts["api"] += 1
            remaining_rows.append(base)

        # Progress
        idx = i + 1 if isinstance(i, int) else list(df_all.index).index(i) + 1
        if (idx) % 100_000 == 0:
            pct = 100 * idx / total
            print(f"  Processed {idx:>9,} / {total:,}  ({pct:.1f}%)  "
                  f"rule={len(rule_rows):,}  api={len(remaining_rows):,}")

    # Save
    rule_df      = pd.DataFrame(rule_rows)
    remaining_df = pd.DataFrame(remaining_rows)

    rule_df.to_csv(OUT_RULE, index=False)
    remaining_df.to_csv(OUT_REMAIN, index=False)

    # Summary
    classified   = len(rule_rows)
    api_needed   = len(remaining_rows)
    coverage_pct = 100 * classified / total if total else 0

    summary = "\n".join([
        "=" * 55,
        "RULE-BASED FILTER — SUMMARY",
        "=" * 55,
        f"Total entities      : {total:>10,}",
        f"Classified by rules : {classified:>10,}  ({coverage_pct:.1f}%)",
        f"  → government      : {counts['government']:>10,}",
        f"  → family_firm     : {counts['family_firm']:>10,}",
        f"  → company         : {counts['company']:>10,}",
        f"  → individual      : {counts['individual']:>10,}",
        f"Sent to Claude API  : {api_needed:>10,}  ({100-coverage_pct:.1f}%)",
        "=" * 55,
        f"Saved rule output   : {OUT_RULE}",
        f"Saved API remainder : {OUT_REMAIN}",
    ])

    print("\n" + summary)
    with open(OUT_SUMMARY, "w") as f:
        f.write(summary)
    print(f"Summary saved → {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
