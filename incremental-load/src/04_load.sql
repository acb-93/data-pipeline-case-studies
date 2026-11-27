-- 04 · Merge into the warehouse and move the watermark (T-SQL)
-- Reads:  outputs/clean_orders.csv — this script loads it into landing.clean_orders itself (BULK INSERT)
-- Reads:  raw/orders.csv — this script loads it into landing.raw_orders itself (BULK INSERT)
-- Writes: scn.FactOrders, scn.etl_watermark

TRUNCATE TABLE landing.clean_orders;
TRUNCATE TABLE landing.raw_orders;
BULK INSERT landing.clean_orders FROM '$(WorkspaceDir)/outputs/clean_orders.csv' WITH(FORMAT = 'CSV', FIRSTROW = 2, FIELDTERMINATOR = ',');
BULK INSERT landing.raw_orders FROM '$(WorkspaceDir)/raw/orders.csv' WITH(FORMAT = 'CSV', FIRSTROW = 2,FIELDTERMINATOR = ',');

DECLARE @LoadFrom datetime2(0) = (SELECT last_loaded_at FROM scn.etl_watermark WHERE source_name = 'orders'),
        @LoadTo       datetime2(0) = (SELECT MAX(loaded_at) FROM landing.raw_orders);

BEGIN TRY
    BEGIN TRAN;
    
UPDATE FO
SET FO.DateKey = DD.DateKey,
    FO.CustomerKey = DC.CustomerKey,
    FO.EmployeeID = CO.employee_id,
    FO.OrderStatus = CO.status,
    FO.Amount = CO.total_amount,
    FO.CurrencyCode = CO.currency_code,
    FO.SourceSystem = CO.source_system
FROM scn.FactOrders AS FO
JOIN landing.clean_orders AS CO ON CO.order_id = FO.OrderID
JOIN dbo.DimCustomer AS DC ON DC.CustomerID = CO.customer_id
JOIN dbo.DimDate AS DD ON DD.FullDate = CO.order_date
WHERE (FO.DateKey IS DISTINCT FROM DD.DateKey
   OR FO.CustomerKey IS DISTINCT FROM DC.CustomerKey 
   OR FO.EmployeeID IS DISTINCT FROM CO.employee_id 
   OR FO.OrderStatus IS DISTINCT FROM CO.status
   OR FO.Amount IS DISTINCT FROM CO.total_amount
   OR FO.CurrencyCode IS DISTINCT FROM CO.currency_code
   OR FO.SourceSystem IS DISTINCT FROM CO.source_system) AND DC.IsCurrent=1;
   
INSERT INTO scn.FactOrders (OrderID,CustomerKey,DateKey,EmployeeID,OrderStatus,Amount,CurrencyCode,SourceSystem)
SELECT CO.order_id,DC.CustomerKey, DD.DateKey, CO.employee_id, CO.status, CO.total_amount, CO.currency_code, CO.source_system FROM dbo.DimCustomer AS DC
JOIN landing.clean_orders AS CO ON CO.customer_id = DC.CustomerID 
JOIN dbo.DimDate AS DD ON DD.FullDate = CO.order_date
WHERE NOT EXISTS (SELECT 1 FROM scn.FactOrders AS FO WHERE FO.OrderID = CO.order_id) AND DC.IsCurrent=1;

UPDATE scn.etl_watermark SET last_loaded_at = COALESCE(@LoadTo,@LoadFrom) WHERE source_name = 'orders';

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
    ROLLBACK TRAN;
    THROW;
END CATCH;

