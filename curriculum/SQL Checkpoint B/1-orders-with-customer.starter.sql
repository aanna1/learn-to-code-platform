-- TODO: the orders table only stores a customer_id number. Join it to `customer`
-- so the report shows the customer's name and city instead of a bare id.
SELECT o.order_id, o.customer_id
FROM sales_order o
ORDER BY o.order_id;
