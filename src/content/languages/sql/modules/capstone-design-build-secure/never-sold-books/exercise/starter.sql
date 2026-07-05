-- This lists EVERY book. You want only the books that have never appeared on
-- an order line -- an absence, which a NOT IN subquery expresses cleanly.
SELECT title FROM book
ORDER BY title;
