SELECT c.name, COALESCE(SUM(oi.quantity * p.price), 0) AS total_spent
FROM customer c
LEFT JOIN sales_order o ON o.customer_id = c.customer_id
LEFT JOIN order_item oi ON oi.order_id = o.order_id
LEFT JOIN product p ON p.product_id = oi.product_id
GROUP BY c.customer_id
ORDER BY c.name;
