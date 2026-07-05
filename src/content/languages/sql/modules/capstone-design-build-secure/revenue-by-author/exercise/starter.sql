-- This uses INNER JOINs, so an author who has sold nothing vanishes entirely.
-- The shop wants the zeros this time -- switch to LEFT JOIN and COALESCE so
-- every author appears, even Octavia Butler (whose only book has never sold).
SELECT a.first_name || ' ' || a.last_name AS author,
       SUM(b.price * ol.quantity) AS revenue
FROM author a
JOIN book b        ON b.author_id = a.author_id
JOIN order_line ol ON ol.book_id = b.book_id
GROUP BY a.author_id, a.first_name, a.last_name
ORDER BY revenue DESC, author;
