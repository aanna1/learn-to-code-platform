-- This joins the three tables but sums the wrong thing -- it counts BOOKS,
-- not money. Multiply price by quantity and total that instead, so each
-- customer's real spend comes back, biggest spender first.
SELECT c.first_name || ' ' || c.last_name AS customer,
       SUM(ol.quantity) AS total_spent
FROM customer c
JOIN book_order bo ON bo.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = bo.order_id
JOIN book b        ON b.book_id = ol.book_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;
