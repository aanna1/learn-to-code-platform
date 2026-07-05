-- TODO: this INNER JOIN lists products that HAVE been ordered — the opposite of
-- what we want. Rewrite it as a LEFT JOIN from product to order_item, then keep
-- only the rows where the order_item side came back empty (oi.product_id IS NULL).
SELECT p.name
FROM product p
JOIN order_item oi ON oi.product_id = p.product_id
ORDER BY p.name;
