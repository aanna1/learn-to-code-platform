-- Outer join all the way down: LEFT JOIN keeps every author even with no sales,
-- and COALESCE turns the resulting NULL sum into a real 0. Swap both LEFT JOINs
-- for inner joins and Butler disappears -- that one-word change is the difference
-- between "our authors' sales" and "authors who have sales."
SELECT a.first_name || ' ' || a.last_name AS author,
       COALESCE(SUM(b.price * ol.quantity), 0) AS revenue
FROM author a
LEFT JOIN book b        ON b.author_id = a.author_id
LEFT JOIN order_line ol ON ol.book_id = b.book_id
GROUP BY a.author_id, a.first_name, a.last_name
ORDER BY revenue DESC, author;
