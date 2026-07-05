-- Starter the learner begins from — must fail >= 1 case.
-- It selects the right columns but forgets to sort and limit, so it returns
-- every product in insertion order instead of the top three by price.
SELECT name, price
FROM products;
