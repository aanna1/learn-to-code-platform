SELECT oi.order_id, SUM(oi.quantity * p.price) AS revenue
FROM order_item oi
JOIN product p ON oi.product_id = p.product_id
GROUP BY oi.order_id
ORDER BY oi.order_id;
