# Few-shot examples to help the model understand how to convert natural language to SQL
SQL_EXAMPLES = [
    {
        "input": "Show the total quantity sold per vegetable category, but only for categories where more than 100 kg were sold.",
        "query": """SELECT c.category_name, SUM(t.qty_sold_kg) AS total_qty_sold
FROM veg_transaction_data t
LEFT JOIN veg_category_data c ON t.item_code = c.item_code
GROUP BY c.category_name
HAVING SUM(t.qty_sold_kg) > 100;"""
    },
    {
        "input": "Calculate the profit margin for each item for August 2020 by comparing transaction data with wholesale prices.",
        "query": """SELECT t.item_code, c.item_name, 
       AVG(ISNULL(w.whsle_px_rmb_kg, 0)) AS avg_whole_sale,
       MAX(ISNULL(w.whsle_px_rmb_kg, 0)) AS max_whole_sale,
       MIN(ISNULL(w.whsle_px_rmb_kg, 0)) AS min_whole_sale,
       (MAX(ISNULL(w.whsle_px_rmb_kg, 0)) - MIN(ISNULL(w.whsle_px_rmb_kg, 0))) AS whole_sale_diff,
       ISNULL(SUM(t.qty_sold_kg * w.whsle_px_rmb_kg), 0) AS whole_sale_price,
       SUM(t.qty_sold_kg * t.unit_selling_px_rmb_perKg) AS selling_price,
       (SUM(t.qty_sold_kg * t.unit_selling_px_rmb_perKg) - ISNULL(SUM(t.qty_sold_kg * w.whsle_px_rmb_kg), 0)) AS profit
FROM veg_transaction_data t
LEFT JOIN veg_wholesale_data w
  ON t.item_code = w.item_code AND t.txn_date = w.whsle_date
LEFT JOIN veg_category_data c
  ON t.item_code = c.item_code
WHERE YEAR(t.txn_date) = 2020 AND MONTH(t.txn_date) = 8
GROUP BY t.item_code, c.item_name;"""
    },
    {
        "input": "Add a new vegetable category called 'Cabbage' with category code 1011010201 for item 'Kohlrabi' with item code '102900051015000'.",
        "query": """IF NOT EXISTS (
    SELECT 1 FROM veg_category_data WHERE item_code = '102900051015000'
)
BEGIN
    INSERT INTO veg_category_data (item_code, item_name, category_code, category_name)
    VALUES ('102900051015000', 'Kohlrabi', '1011010201', 'Cabbage');
END
ELSE
BEGIN
    UPDATE veg_category_data
    SET item_name = 'Kohlrabi'
    WHERE item_code = '102900051015000';
END"""
    },
    {
        "input": "On 2020-08-10, the shop received a shipment of 500kg of 'Spinach' (item code: '102900005118817') at 3.5 RMB per kg. Update inventory and add a wholesale record.",
        "query": """-- Insert wholesale shipment
BEGIN TRANSACTION;

-- Insert wholesale shipment
INSERT INTO veg_wholesale_data (whsle_date, item_code, whsle_px_rmb_kg)
VALUES ('2020-08-10', '102900005118817', 3.5);

-- Insert category if it does not exist
IF NOT EXISTS (
    SELECT 1 FROM veg_category_data WHERE item_code = '102900005118817'
)
BEGIN
    INSERT INTO veg_category_data (item_code, item_name, category_code, category_name)
    VALUES ('102900005118817', 'Spinach', '1011010301', 'Leafy Vegetables');
END

COMMIT TRANSACTION;
"""
    },
    
    {
        "input": "A customer returned 5kg of 'Caixin' (item code: '102900005115908') from a purchase made on 2020-09-15.",
        "query": """INSERT INTO veg_transaction_data (txn_date, txn_time, item_code, qty_sold_kg, unit_selling_px_rmb_perKg, sale_or_return, discount_perc, day_of_week)
VALUES (
  '2020-09-16', 
  '11:00:00', 
  '102900005115908', 
  -5, 
  (SELECT TOP 1 unit_selling_px_rmb_perKg 
   FROM veg_transaction_data 
   WHERE item_code = '102900005115908' 
   ORDER BY txn_date DESC), 
  'RETURN', 0, 'Wednesday');"""
    },

    {
        "input": "Show me all the tables in the database.",
        "query": """SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';"""
    },
    {
        "input": "List the names of all tables available.",
        "query": """SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';"""
    },
    {
        "input": "How many tables are there in the database?",
        "query": """SELECT COUNT(*) AS total_tables
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';"""
    },
    {
        "input": "What columns are in the table veg_transaction_data?",
        "query": """SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'veg_transaction_data';"""
    },
    {
        "input": "Give me the schema for veg_category_data.",
        "query": """SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'veg_category_data';"""
    },
    {
        "input": "List all columns and their data types for the table loss_rate_data.",
        "query": """SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'loss_rate_data';"""
    },
    {
        "input": "What are the primary keys of each table?",
        "query": """SELECT 
    KU.TABLE_NAME,
    KU.COLUMN_NAME,
    KU.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE KU
    ON TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME
WHERE TC.CONSTRAINT_TYPE = 'PRIMARY KEY';"""
    },
    {
        "input": "Which tables reference veg_category_data?",
        "query": """SELECT 
    fk.name AS foreign_key_name,
    tp.name AS parent_table,
    cp.name AS parent_column,
    tr.name AS referenced_table,
    cr.name AS referenced_column
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
WHERE tr.name = 'veg_category_data';"""
    },
    {
        "input": "Does the table veg_wholesale_data have a foreign key?",
        "query": """SELECT 
    f.name AS foreign_key_name, 
    OBJECT_NAME(f.parent_object_id) AS table_name, 
    COL_NAME(fc.parent_object_id,fc.parent_column_id) AS column_name, 
    OBJECT_NAME (f.referenced_object_id) AS referenced_table_name
FROM sys.foreign_keys AS f
INNER JOIN sys.foreign_key_columns AS fc 
    ON f.object_id = fc.constraint_object_id
WHERE OBJECT_NAME(f.parent_object_id) = 'veg_wholesale_data';"""
    },
    {
        "input": "Which item has the highest loss rate percentage?",
        "query": """SELECT TOP 1 item_code, item_name, loss_rate_perc
FROM loss_rate_data
ORDER BY loss_rate_perc DESC;"""
    },
    {
        "input": "List all items in the 'Edible Mushroom' category.",
        "query": """SELECT item_code, item_name
FROM veg_category_data
WHERE category_name = 'Edible Mushroom';"""
    },
    {
        "input": "What is the category of 'Xixia Black Mushroom (1)'?",
        "query": """SELECT category_name
FROM veg_category_data
WHERE item_name = 'Xixia Black Mushroom (1)';"""
    },
    {
        "input": "Show sales data for 'Niushou Shengcai' on July 1, 2020.",
        "query": """SELECT txn_date, txn_time, qty_sold_kg, unit_selling_px_rmb_perKg
FROM veg_transaction_data
WHERE item_code = '102900005115168' AND txn_date = '2020-07-01';"""
    },
    {
        "input": "What was the average wholesale price of 'Sichuan Red Cedar' in July 2020?",
        "query": """SELECT AVG(whsle_px_rmb_kg) AS avg_wholesale_price
FROM veg_wholesale_data
WHERE item_code = '102900005115199' AND MONTH(whsle_date) = 7 AND YEAR(whsle_date) = 2020;"""
    },
    {
        "input": "Which items were sold on July 1, 2020, and how much was sold?",
        "query": """SELECT t.item_code, c.item_name, SUM(t.qty_sold_kg) AS total_sold
FROM veg_transaction_data t
JOIN veg_category_data c ON t.item_code = c.item_code
WHERE t.txn_date = '2020-07-01'
GROUP BY t.item_code, c.item_name;"""
    },
    {
        "input": "Add a new vegetable category called 'Root Vegetables' with code '1011010901' for item 'Carrot' with item code '102900005199999'.",
        "query": """IF NOT EXISTS (
    SELECT 1 FROM veg_category_data WHERE item_code = '102900005199999'
)
BEGIN
    INSERT INTO veg_category_data (item_code, item_name, category_code, category_name)
    VALUES ('102900005199999', 'Carrot', '1011010901', 'Root Vegetables');
END"""
    },
    {
        "input": "A customer returned 2 kg of 'Sichuan Red Cedar' bought on 2020-07-01.",
        "query": """INSERT INTO veg_transaction_data (txn_date, txn_time, item_code, qty_sold_kg, unit_selling_px_rmb_perKg, sale_or_return, discount_perc, day_of_week)
VALUES (
  '2020-07-02', 
  '10:00:00', 
  '102900005115199', 
  -2, 
  (SELECT TOP 1 unit_selling_px_rmb_perKg 
   FROM veg_transaction_data 
   WHERE item_code = '102900005115199' 
   ORDER BY txn_date DESC), 
  'RETURN', 0, 'Thursday');"""
    }

]
