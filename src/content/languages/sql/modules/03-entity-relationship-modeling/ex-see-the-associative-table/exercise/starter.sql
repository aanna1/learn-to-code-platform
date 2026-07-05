-- This query shows the projects — but not who is working on them. The projects
-- table can't tell you the pairings; a project row has no room to list every
-- employee on it. That's exactly the job of the associative entity.
-- TODO: query the assignment table instead, so the grid shows every
-- employee-project pairing. Return all of its columns.
SELECT * FROM project;
