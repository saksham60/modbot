# UI Design

The UI is a moderation operations console rather than a generic playground.

## Main Regions

- top bar with task overview
- task/seed controls
- metrics strip for trust, appeals, backlog, budget, return, and final score
- queue table
- current report panel
- fetched context panel
- operator feed
- trajectory log
- episode summary

## Interaction Model

- `Reset Episode` starts a seeded run
- `Step Action` applies one typed action
- `Auto-Run Baseline` runs the heuristic policy to completion

## Separation

- page composition lives in `app/ui/pages/`
- event/session orchestration lives in `app/ui/services/`
- pure formatting lives in `app/ui/components/`
