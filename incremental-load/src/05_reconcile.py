"""
05 · Reconcile (Python)

Reads:  raw/orders.csv, outputs/clean_orders.csv, quarantine/rejected_orders.csv, scn.FactOrders, scn.etl_watermark
Writes: outputs/reconciliation_report.json
"""

import pandas as pd
import json

#---Read CSV Files---#

raw_orders = pd.read_csv("raw/orders.csv")
clean_orders = pd.read_csv("outputs/clean_orders.csv")
rejected_orders = pd.read_csv("quarantine/rejected_orders.csv")
loaded_orders = pd.read_csv("outputs/loaded_orders.csv")
watermark_df = pd.read_csv("outputs/etl_watermark.csv")

#---Calculate Row Counts & Watermark---#

source_rows = raw_orders["order_id"].size
accepted_rows = clean_orders["order_id"].size
rejected_rows = rejected_orders["order_id"].size
fact_rows = loaded_orders["OrderID"].size
watermark = watermark_df["last_loaded_at"].iloc[0]

#---Define Reconciliation Checks---#

source_balances = source_rows == accepted_rows + rejected_rows
combined = clean_orders.merge(loaded_orders, left_on = "order_id", right_on = "OrderID", how = "left", indicator=True) 
accepted_in_fact = bool((combined["_merge"].value_counts()["both"] == accepted_rows) and (abs(combined["total_amount"] - combined["Amount"])<= 0.01).all())
watermark_is_latest = bool(raw_orders.empty or watermark == raw_orders["loaded_at"].max())

#---Export to Report---#

report = {"source_rows" : source_rows, "accepted_rows" : accepted_rows, "rejected_rows" : rejected_rows, "fact_rows" : fact_rows, "source_balances" : source_balances, "accepted_in_fact" : accepted_in_fact, "watermark" : watermark, "watermark_is_latest" : watermark_is_latest}

with open ("outputs/reconciliation_report.json", "w" , encoding="utf-8") as f:
    json.dump(report,f,indent=2)





