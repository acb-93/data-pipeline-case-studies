"""
05 · Reconcile (Python)

Reads:  raw/customers.csv, outputs/clean_customers.csv, quarantine/rejected_customers.csv, scn.DimCustomer
Writes: outputs/reconciliation_report.json
"""

import pandas as pd
import json

#---Read CSV Files---#

df_raw = pd.read_csv("raw/customers.csv")
df_clean = pd.read_csv("outputs/clean_customers.csv")
df_quarantine = pd.read_csv("quarantine/rejected_customers.csv")
df_dim = pd.read_csv("outputs/dim_customers.csv")

#---Calculate Row Counts---#

source_rows = len(df_raw)
accepted_rows = len(df_clean)
rejected_rows = len(df_quarantine)
dimension_rows = len(df_dim)
current_rows = int(df_dim["IsCurrent"].eq(1).sum())

#---Classify Today's Customers---#

summary = df_dim.groupby("CustomerID").agg(version_count = ("CustomerID", "size"), new_ver=("EffectiveDate", lambda s: s.eq("2024-07-01").any()))
summary = summary[summary.index.isin(df_clean["customer_id"])]
new_customers = int((summary["new_ver"] & summary["version_count"].eq(1)).sum())
changed_customers = int((summary["new_ver"] & summary["version_count"].gt(1)).sum())
unchanged_customers = int((~summary["new_ver"]).sum())

#---Define Reconciliation Checks---#

source_balances = source_rows == accepted_rows + rejected_rows
current_per_customer = df_dim.groupby("CustomerID")["IsCurrent"].apply(lambda s: s.eq(1).sum())
one_current_per_customer = bool(current_per_customer.eq(1).all())

#---Export to Report---#

report = {"source_rows" : source_rows, "accepted_rows" : accepted_rows, "rejected_rows" : rejected_rows, "source_balances" : source_balances, "new_customers" : new_customers, "changed_customers" : changed_customers, "unchanged_customers" : unchanged_customers, "dimension_rows" : dimension_rows, "current_rows" : current_rows, "one_current_per_customer" : one_current_per_customer}

with open ("outputs/reconciliation_report.json", "w" , encoding="utf-8") as f:
    json.dump(report,f,indent=2)


