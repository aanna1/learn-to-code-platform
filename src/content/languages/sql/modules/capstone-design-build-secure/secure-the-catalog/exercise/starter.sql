-- This view is SELECT * FROM book, so it leaks book_id, genre, and author_id --
-- and shows an author id instead of a name. Rebuild it to expose exactly the
-- public catalog: title, the author's full name, and price. Join to author.
CREATE VIEW catalog_public AS
SELECT * FROM book;

SELECT * FROM catalog_public ORDER BY title;
