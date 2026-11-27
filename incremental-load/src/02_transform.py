"""
02 · Clean and validate (pandas)

Writes: raw/orders.csv, outputs/clean_orders.csv, quarantine/rejected_orders.csv
"""

import pandas as pd
import os
import pyodbc

#---Read from SQL to DataFrame---#

s1 = pyodbc.connect(os.environ["PIPELINEFAB_SOURCE_CONNECTION"])
q_s1 = open("code/s1_extract.sql", encoding="utf-8").read()
df = pd.read_sql(q_s1,s1)
s1.close()
df.to_csv("raw/orders.csv",index=False)
df_raw = df.copy()

#---Data Manipulations and Masks---#

df["order_id"] = pd.to_numeric(df["order_id"], errors = "coerce")
df["customer_id"] = pd.to_numeric(df["customer_id"], errors = "coerce")
df["total_amount"] = pd.to_numeric(df["total_amount"], errors = "coerce")
valid_order_id = df["order_id"].notna()
valid_customer_id = df["customer_id"].notna()
valid_amount = df["total_amount"] > 0
valid_order_status = df["status"].isin(["Pending","Processing","Shipped","Delivered","Cancelled"])
df["order_date_converted"] = pd.to_datetime(df["order_date"], format="mixed",dayfirst=False, errors="coerce")
df["order_date"] = pd.to_datetime(df["order_date_converted"], format="%Y-%m-%d")
valid_date = df["order_date_converted"].notna()
duplicated_orders = df["order_id"].duplicated(keep="first")

#---Define Reject Reasons & DataFrame---#

reject_flags = pd.DataFrame({"Invalid OrderID" : ~valid_order_id,"Duplicated Order" : duplicated_orders, "Invalid CustomerID" : ~valid_customer_id, "Invalid Order Date" : ~valid_date,"Invalid Order Status" : ~valid_order_status, "Invalid Amount" : ~valid_amount})
reason = reject_flags.apply(lambda row: ", ".join(row.index[row]), axis=1, result_type = "reduce")

#---Create Clean & Rejected DataFrames---#

df_rejected = df_raw.loc[reject_flags.any(axis=1)].copy()
df_rejected["reject_reason"] = reason
df_clean = df.loc[~reject_flags.any(axis=1)].copy()
df_clean["customer_id"] = df_clean["customer_id"].astype("Int64")

#---Export to CSV---#

df_clean.rename(columns={"currency" : "currency_code"}).to_csv("outputs/clean_orders.csv",index=False,float_format="%.2f", columns=["order_id","customer_id","employee_id","order_date","status","total_amount","currency_code","source_system"])

df_rejected.to_csv("quarantine/rejected_orders.csv",index=False)



