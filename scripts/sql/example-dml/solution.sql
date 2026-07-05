-- Reference answer — raise the price of every 'office' product by 10.
-- The WHERE clause is the whole point: only office rows should change.
UPDATE products
SET price = price + 10
WHERE category = 'office';
