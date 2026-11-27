-- 01 · Extract tonight's orders (since the watermark) (T-SQL)
-- The result is not written to a file here: stage 02 runs this query itself (pyodbc) and writes the extract file.
-- Runs in a transaction that is rolled back: the source is never changed.

SELECT order_id, customer_id, employee_id, order_date, status, total_amount, currency, source_system, loaded_at FROM scn.orders_feed 
WHERE loaded_at > (SELECT last_loaded_at FROM DW.scn.etl_watermark
                   WHERE source_name = 'orders')

