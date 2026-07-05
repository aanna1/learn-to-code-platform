-- Revenue lives in three tables at once (who ordered, what was on the order,
-- what it cost), so it's a three-join chain feeding an aggregate. An INNER JOIN
-- is right here: "spent" implies at least one purchase, so Leo (no orders) drops.
SELECT c.first_name || ' ' || c.last_name AS customer,
       ROUND(SUM(b.price * ol.quantity), 2) AS total_spent
FROM customer c
JOIN book_order bo ON bo.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = bo.order_id
JOIN book b        ON b.book_id = ol.book_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;
