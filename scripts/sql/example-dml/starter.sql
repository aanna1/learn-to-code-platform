-- Starter — must fail >= 1 case. It raises EVERY product's price because it
-- forgets the WHERE clause, so it also changes the 'home' products it shouldn't.
UPDATE products
SET price = price + 10;
