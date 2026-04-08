# Grading Design

ModBot uses deterministic final graders separate from dense rewards.

## Easy

- emphasizes exact action correctness
- includes queue completion and final trust

## Medium

- emphasizes action accuracy, severe-violation recall, and removal precision
- explicitly scores context discipline on ambiguous cases
- includes appeal control to punish over-enforcement

## Hard

- emphasizes severe-violation recall under operational pressure
- balances removal precision, queue efficiency, trust preservation, and backlog control

## Determinism

- graders consume final hidden state only
- task fixtures are loaded from static JSON
- seeded queue ordering is reproducible
- grader outputs are stable for identical trajectories
