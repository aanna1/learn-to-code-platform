SELECT o.order_id, c.name, c.city
FROM sales_order o
JOIN customer c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
