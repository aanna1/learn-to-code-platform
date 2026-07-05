-- The public catalog page needs titles, authors, and prices -- never the
-- customer or staff tables. A view makes that boundary the database's job:
-- GRANT SELECT on catalog_public and REVOKE the base tables, and the storefront
-- is structurally incapable of leaking a customer's email or a staff login.
CREATE VIEW catalog_public AS
SELECT b.title,
       a.first_name || ' ' || a.last_name AS author,
       b.price
FROM book b
JOIN author a ON a.author_id = b.author_id;

SELECT * FROM catalog_public ORDER BY title;
