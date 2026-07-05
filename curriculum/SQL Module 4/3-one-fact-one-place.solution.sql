-- Three branches, three rows — "Scranton" appears exactly once, even though two
-- orders are placed there. The orders table just stores branch_id 2 and points
-- here. Rename Scranton in this one row and every order that references it is
-- "updated" for free: there was never a second copy to forget. That's the whole
-- payoff of 3NF — one fact, one place.
SELECT branch_id, city FROM branch;
