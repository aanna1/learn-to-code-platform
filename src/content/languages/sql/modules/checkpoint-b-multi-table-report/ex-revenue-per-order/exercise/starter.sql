-- TODO: each order_item row has a quantity, but the PRICE lives in the product
-- table. Join order_item to product, multiply quantity * price, and SUM per order.
-- Right now this just counts line items and never touches price.
SELECT oi.order_id, COUNT(*) AS revenue
FROM order_item oi
GROUP BY oi.order_id
ORDER BY oi.order_id;
