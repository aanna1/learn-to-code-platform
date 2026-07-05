-- The subquery collects every book_id that appears on any order line; the outer
-- query keeps the books NOT in that set. order_line.book_id is NOT NULL, so the
-- classic NOT IN null-trap can't bite here (NOT EXISTS is the sturdier choice
-- whenever the subquery column might be nullable).
SELECT title FROM book
WHERE book_id NOT IN (SELECT book_id FROM order_line)
ORDER BY title;
