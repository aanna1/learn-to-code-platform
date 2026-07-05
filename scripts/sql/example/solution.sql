-- Reference answer — must pass every case in tests.json.
-- The three most expensive products, priciest first.
SELECT name, price
FROM products
ORDER BY price DESC
LIMIT 3;
