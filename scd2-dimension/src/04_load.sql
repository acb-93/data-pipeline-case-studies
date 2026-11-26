-- 04 · Apply the snapshot to the customer dimension (T-SQL)
-- Reads:  outputs/clean_customers.csv — this script loads it into landing.clean_customers itself (BULK INSERT)
-- Writes: scn.DimCustomer

TRUNCATE TABLE landing.clean_customers;
BULK INSERT landing.clean_customers FROM '$(WorkspaceDir)\outputs\clean_customers.csv' 
WITH (FORMAT = 'CSV',FIRSTROW = 2, FIELDTERMINATOR = ',',
      ROWTERMINATOR = '\n', CODEPAGE = '65001');
      
DECLARE @LoadDate date = '2024-07-01';

SET XACT_ABORT ON;
BEGIN TRY;
    BEGIN TRAN;
        UPDATE d SET d.IsCurrent = 0, d.ExpiryDate = DATEADD(DAY,-1,@LoadDate) FROM scn.DimCustomer AS d
        INNER JOIN landing.clean_customers AS cl ON cl.customer_id = d.CustomerID
        WHERE d.IsCurrent = 1 AND (d.Country IS DISTINCT FROM cl.Country OR d.City IS DISTINCT FROM
        cl.City OR d.CreditTier IS DISTINCT FROM cl.credit_tier);
        
        INSERT INTO scn.DimCustomer (CustomerID, CompanyName, ContactName, Country, City,
        CreditTier, EffectiveDate, ExpiryDate, IsCurrent)
        SELECT DISTINCT cl.customer_id, cl.company_name, cl.contact_name, cl.country, cl.city,
        cl.credit_tier,@LoadDate,NULL, 1
        FROM landing.clean_customers AS cl
        WHERE NOT EXISTS (SELECT 1 FROM scn.DimCustomer AS d
                          WHERE d.CustomerID = cl.customer_id AND d.IsCurrent = 1);
                          
        UPDATE d
        SET d.CompanyName = cl.company_name,
            d.ContactName = cl.contact_name
            FROM scn.DimCustomer AS d
            INNER JOIN landing.clean_customers AS CL ON cl.customer_id = d.CustomerID
            WHERE (d.CompanyName IS DISTINCT FROM cl.company_name OR
                  d.ContactName IS DISTINCT FROM cl.contact_name) AND d.IsCurrent = 1
    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRAN;
    THROW;
END CATCH
        


  
        
      
    
