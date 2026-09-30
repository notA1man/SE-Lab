# Endless Runner - Lab 4

Requires Python 3.10+. Install with `pip install -r requirements.txt`, then
run `python main.py`. Jump with Space, Up, or W; exit with Esc.

## Task 1: Collision detection

Implemented time-based movement, physics substeps, swept rectangle collision
checks, and a maximum speed. Obstacles cannot skip across the player without
registering a hit. Scoring occurs only after a safe clearance.

## Task 2: Game over

Collision freezes the run and opens a final-score screen with graceful exit.
Added a neon skyline, stable parallax scrolling, brief jump dust, score flash,
and pause/resume with P or Esc.

Upcoming tasks: replay/difficulty selection and sound feedback.
