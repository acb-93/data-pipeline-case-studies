-- 01 · Extract today's customer snapshot (T-SQL)
-- Result sets, in order: raw/customers.csv
-- Runs in a transaction that is rolled back: the source is never changed.

-- S1 - Extract today's customer snapshot
-- Database: Staging
SELECT
    customer_id,
    company_name,
    contact_name,
    country,
    city,
    credit_limit,
    loaded_at
FROM scn.customers_snapshot;
