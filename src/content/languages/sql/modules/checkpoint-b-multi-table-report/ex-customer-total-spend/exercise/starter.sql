-- TODO: this uses INNER JOINs, so a customer who has never ordered anything
-- (Dave) vanishes from the report entirely. Switch the joins to LEFT JOIN so
-- every customer appears, and wrap the SUM in COALESCE(..., 0) so a customer
-- with no orders shows 0 instead of NULL.
SELECT c.name, SUM(oi.quantity * p.price) AS total_spent
FROM customer c
JOIN sales_order o ON o.customer_id = c.customer_id
JOIN order_item oi ON oi.order_id = o.order_id
JOIN product p ON p.product_id = oi.product_id
GROUP BY c.customer_id
ORDER BY c.name;
