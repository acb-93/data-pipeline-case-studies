"""
02 · Clean and validate (pandas)

Reads:  raw/customers.csv
Writes: outputs/clean_customers.csv, quarantine/rejected_customers.csv
"""

import pandas as pd
import numpy as np

#---Read CSV to DataFrame---#

df = pd.read_csv("raw/customers.csv",dtype=str, keep_default_na=False)
df_raw = df.copy()

#---Data Manipulations and Masks---#

df["customer_id"] = pd.to_numeric(df["customer_id"], errors ="coerce")
df["credit_limit"] = pd.to_numeric(df["credit_limit"], errors ="coerce")
str_columns = ["company_name","contact_name","country","city"]
df[str_columns] = df[str_columns].apply(lambda col:col.str.strip())
df["country"] = df["country"].replace(["USA","U.S.","UK","Great Britain","Deutschland","Holland","Korea","Espana"],["United States","United States","United Kingdom","United Kingdom","Germany","Netherlands","South Korea","Spain"])

df["credit_tier"] = np.select([df["credit_limit"] >= 50000, df["credit_limit"] >=20000 , df["credit_limit"]>=5000],["Platinum","Gold","Silver"], default = "Bronze")

df["loaded_at"] = pd.to_datetime(df["loaded_at"])
df = df.sort_values("loaded_at",ascending=False)
duplicate = df["customer_id"].duplicated(keep="first")
empty_country = df["country"].isna() | df["country"].eq("")
empty_customer_id = df["customer_id"].isna()

#---Define Reject Reasons & DataFrame---#

errors = pd.DataFrame({"invalid_customer_id" : empty_customer_id , "missing_country" : empty_country , "old_record" : duplicate & df["customer_id"].notna()})
reasons = errors.apply(lambda row:";".join(row.index[row]), axis=1)

#---Create Clean & Rejected DataFrames---#

df_rejected = df_raw.loc[duplicate | empty_country |empty_customer_id].copy()
df_rejected["reject_reason"] = reasons

#---Export to CSV---#

df.loc[~duplicate & ~empty_country & ~empty_customer_id].sort_values("customer_id").to_csv("outputs/clean_customers.csv",index=False, columns=["customer_id","company_name","contact_name","country","city","credit_tier"])
df_rejected.to_csv("quarantine/rejected_customers.csv", index=False)
