"""
02 · Clean and validate (pandas)

Reads:  raw/customers.csv
Writes: outputs/clean_customers.csv, quarantine/rejected_customers.csv
"""

import os
import pandas as pd

RAW_COLUMNS = [
    "customer_id", "company_name", "contact_name", "country",
    "city", "credit_limit", "loaded_at",
]
CLEAN_COLUMNS = [
    "customer_id", "company_name", "contact_name",
    "country", "city", "credit_tier",
]
COUNTRY_ALIASES = {
    "USA": "United States",
    "U.S.": "United States",
    "UK": "United Kingdom",
    "Great Britain": "United Kingdom",
    "Deutschland": "Germany",
    "Holland": "Netherlands",
    "Korea": "South Korea",
    "Espana": "Spain",
}


def main():
    # Keep every source field as text to preserve its original format.
    raw = pd.read_csv("raw/customers.csv", dtype=str, keep_default_na=False)
    assert raw.columns.tolist() == RAW_COLUMNS, "Unexpected columns in the S1 CSV"

    # Keep the first exact copy; customer IDs must contain only digits.
    exact_duplicate = raw.duplicated(subset=RAW_COLUMNS, keep="first")
    numeric_id = raw["customer_id"].str.strip().str.fullmatch(r"\d+", na=False)

    early_reject = raw.loc[exact_duplicate | ~numeric_id, RAW_COLUMNS].copy()
    early_reject["reject_reason"] = "customer_id is missing or not numeric"
    early_reject.loc[exact_duplicate, "reject_reason"] = "duplicate copy"

    candidates = raw.loc[~exact_duplicate & numeric_id, RAW_COLUMNS].copy()
    candidates["_customer_id"] = candidates["customer_id"].str.strip().astype("int64")

    # Convert timestamps to datetime before sorting.
    candidates["_loaded_at"] = pd.to_datetime(
        candidates["loaded_at"].str.strip(),
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )

    # Quarantine older versions of the same customer.
    # If timestamps match, keep the last row in source order.
    candidates["_source_order"] = candidates.index
    ordered = candidates.sort_values(["_customer_id", "_loaded_at", "_source_order"])
    superseded = ordered.duplicated(subset="_customer_id", keep="last")

    old_reject = ordered.loc[superseded, RAW_COLUMNS].copy()
    old_reject["reject_reason"] = "superseded by a newer version"

    latest = ordered.loc[~superseded].copy()

    # Trim text fields and standardize known country names.
    for column in ["company_name", "contact_name", "country", "city", "credit_limit"]:
        latest[column] = latest[column].str.strip()

    latest["country"] = latest["country"].map(COUNTRY_ALIASES).fillna(latest["country"])

    # Flag invalid values without changing the original source rows.
    missing_country = latest["country"].eq("")

    credit_ok = latest["credit_limit"].eq("") | latest["credit_limit"].str.fullmatch(
        r"\d+(?:\.\d{1,2})?", na=False
    )

    invalid_credit = ~credit_ok
    wrong = missing_country | invalid_credit

    latest["reject_reason"] = ""
    latest.loc[missing_country, "reject_reason"] = "country is missing"
    latest.loc[invalid_credit, "reject_reason"] = "credit_limit is not a valid amount"

    latest.loc[missing_country & invalid_credit, "reject_reason"] = (
        "country is missing; credit_limit is not a valid amount"
    )

    # Use the original source values for rejected rows.
    # This preserves original spacing and country names in quarantine.
    late_reject = raw.loc[latest.loc[wrong].index, RAW_COLUMNS].copy()
    late_reject["reject_reason"] = latest.loc[wrong, "reject_reason"]

    clean = latest.loc[~wrong].copy()

    # Assign credit tiers with vectorized interval checks.
    limit = pd.to_numeric(clean["credit_limit"].replace("", "0"), errors="raise")

    clean["credit_tier"] = pd.cut(
        limit,
        bins=[-1, 5000, 20000, 50000, float("inf")],
        right=False,
        labels=["Bronze", "Silver", "Gold", "Platinum"],
    ).astype(str)

    clean["customer_id"] = clean["_customer_id"].astype(str)
    clean = clean[CLEAN_COLUMNS].copy()

    rejected = pd.concat(
        [early_reject, old_reject, late_reject], ignore_index=True
    )[RAW_COLUMNS + ["reject_reason"]]

    # Check row conservation, unique keys, and accepted data quality.
    assert len(raw) == len(clean) + len(rejected), "Source rows do not balance"
    assert clean["customer_id"].is_unique, "Duplicate customer IDs in accepted data"
    assert (clean["country"] != "").all(), "Missing country in accepted data"
    assert clean["credit_tier"].isin(["Bronze", "Silver", "Gold", "Platinum"]).all()

    # Write to temporary files before replacing the final outputs.
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("quarantine", exist_ok=True)

    clean.to_csv("outputs/clean_customers.csv.tmp", index=False)
    rejected.to_csv(
        "quarantine/rejected_customers.csv.tmp", index=False
    )

    # Read the temporary outputs back to verify row counts and columns.
    check_clean = pd.read_csv(
        "outputs/clean_customers.csv.tmp", dtype=str, keep_default_na=False
    )

    check_rejected = pd.read_csv(
        "quarantine/rejected_customers.csv.tmp", dtype=str, keep_default_na=False
    )

    assert len(check_clean) == len(clean) and check_clean.columns.tolist() == CLEAN_COLUMNS
    assert len(check_rejected) == len(rejected)
    assert check_rejected.columns.tolist() == RAW_COLUMNS + ["reject_reason"]

    os.replace("outputs/clean_customers.csv.tmp", "outputs/clean_customers.csv")
    os.replace("quarantine/rejected_customers.csv.tmp", "quarantine/rejected_customers.csv")

    print(f"S2: source={len(raw)} accepted={len(clean)} rejected={len(rejected)}")


if __name__ == "__main__":
    main()

