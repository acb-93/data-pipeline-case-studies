-- 04 · Apply the snapshot to the customer dimension (T-SQL)
-- Reads:  landing.clean_customers — outputs/clean_customers.csv loaded into SQL Server before this script runs
-- Writes: scn.DimCustomer

-- S4 - Apply the snapshot to the customer dimension
-- Database: DW

DECLARE @BatchDate DATE = DATEFROMPARTS(2024, 7, 1);

-- Type 2: close CURRENT rows whose tracked attributes changed.
UPDATE d
SET d.ExpiryDate = DATEADD(DAY, -1, @BatchDate), d.IsCurrent = 0
FROM scn.DimCustomer AS d
INNER JOIN landing.clean_customers AS s ON s.customer_id = d.CustomerID
WHERE d.IsCurrent = 1
  AND (d.Country <> s.country
       OR ISNULL(d.City, N'') <> ISNULL(s.city, N'')
       OR d.CreditTier <> s.credit_tier);

-- Add first-time customers and customers whose prior version was closed.
INSERT INTO scn.DimCustomer (
    CustomerID, CompanyName, ContactName, Country, City, CreditTier,
    EffectiveDate, ExpiryDate, IsCurrent
)
SELECT s.customer_id, s.company_name, s.contact_name,
       s.country, s.city, s.credit_tier, @BatchDate, NULL, 1
FROM landing.clean_customers AS s
WHERE NOT EXISTS (
    SELECT 1 FROM scn.DimCustomer AS d
    WHERE d.CustomerID = s.customer_id AND d.IsCurrent = 1
);

-- Type 1: correct names IN PLACE on current versions.
UPDATE d
SET d.CompanyName = s.company_name, d.ContactName = s.contact_name
FROM scn.DimCustomer AS d
INNER JOIN landing.clean_customers AS s ON s.customer_id = d.CustomerID
WHERE d.IsCurrent = 1
  AND (d.CompanyName <> s.company_name
       OR ISNULL(d.ContactName, N'') <> ISNULL(s.contact_name, N''));
