"""
05 · Reconcile (Python)

Reads:  raw/customers.csv, outputs/clean_customers.csv, quarantine/rejected_customers.csv, scn.DimCustomer
Writes: outputs/reconciliation_report.json
"""

import json
import os
import pandas as pd

BATCH_DATE = "2024-07-01"


def normalize_customer_id(values):
    """Normalize numeric customer IDs, so '001' and '1' are treated alike."""
    result = values.str.strip().copy()
    numeric = result.str.fullmatch(r"\d+", na=False)
    result.loc[numeric] = result.loc[numeric].astype("int64").astype(str)
    return result


def main():
    # Read business keys as text to avoid losing leading zeros.
    source = pd.read_csv("raw/customers.csv", dtype=str, keep_default_na=False)
    accepted = pd.read_csv("outputs/clean_customers.csv", dtype=str, keep_default_na=False)
    rejected = pd.read_csv("quarantine/rejected_customers.csv", dtype=str, keep_default_na=False)
    dimension = pd.read_csv("outputs/dim_customers.csv", dtype=str, keep_default_na=False)

    for df, column in [
        (source, "customer_id"), (accepted, "customer_id"),
        (rejected, "customer_id"), (dimension, "CustomerID"),
    ]:
        df["_key"] = normalize_customer_id(df[column])

    # Confirm row counts match for each business key.
    count_by_key = pd.concat(
        [
            source.groupby("_key").size().rename("source"),
            accepted.groupby("_key").size().rename("accepted"),
            rejected.groupby("_key").size().rename("rejected"),
        ],
        axis=1,
    ).fillna(0)
    source_balances = bool(
        len(source) == len(accepted) + len(rejected)
        and (count_by_key["source"] == count_by_key["accepted"] + count_by_key["rejected"]).all()
    )

    # Separate records added in this batch from older versions.
    version_count = dimension.groupby("_key").size()
    today_keys = dimension.loc[
        (dimension["EffectiveDate"].str[:10] == BATCH_DATE), "_key"
    ]
    has_today = accepted["_key"].isin(today_keys)
    has_older_version = (accepted["_key"].map(version_count) > 1)
    new_customers = int((has_today & ~has_older_version).sum())
    changed_customers = int((has_today & has_older_version).sum())
    unchanged_customers = int(len(accepted) - new_customers - changed_customers)

    # Each customer must have exactly one current dimension row.
    current = dimension.loc[(dimension["IsCurrent"] == "1")]
    current_per_key = current.groupby("_key").size()
    one_current_per_customer = bool(
        len(current_per_key) == len(version_count) and (current_per_key == 1).all()
    )

    report = {
        "source_rows": int(len(source)),
        "accepted_rows": int(len(accepted)),
        "rejected_rows": int(len(rejected)),
        "source_balances": source_balances,
        "new_customers": new_customers,
        "changed_customers": changed_customers,
        "unchanged_customers": unchanged_customers,
        "dimension_rows": int(len(dimension)),
        "current_rows": int(len(current)),
        "one_current_per_customer": one_current_per_customer,
    }

    # Write the report to a temporary file, then replace the final file.
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/reconciliation_report.json.tmp", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
    os.replace("outputs/reconciliation_report.json.tmp", "outputs/reconciliation_report.json")
    print(report)


if __name__ == "__main__":
    main()
