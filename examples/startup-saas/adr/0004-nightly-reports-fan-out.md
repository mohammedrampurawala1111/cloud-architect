# ADR-0004: Generate nightly reports with an hourly sweep and per-company jobs

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Customers across about 5 US and Canadian time zones expect reports ready at the start of their working day. Reports must not slow down the interactive API. There is no on-call, so failures must retry on their own and surface in the morning.

## Decision drivers
- Time zones differ per company.
- Function time limit (15 minutes) and database load.
- Failure isolation: one company's failure must not block others.
- Team-fit: no workflow engine to run.

## Options considered
1. **Hourly scheduler → planner → one queue message per company → worker.**
2. One global nightly job looping over companies: a single failure or timeout stops everything; wrong hour for most zones.
3. A managed workflow/state-machine service: more capable, but another concept for the team; not needed yet.
4. Scheduled container task (Option B component): no time limit; held back as the fallback.

## Decision
We chose **an hourly scheduler that finds companies whose local time is 01:00 and have no report for today, enqueues one job per company, and a worker that produces the file in object storage and queues an email**, because it isolates failures per company, handles time zones with one rule, and needs no extra components beyond the queue we already have. Jobs are idempotent (key: company + local date), queries run with a statement timeout, and failed jobs land in a dead-letter queue.

## Consequences
- Pros: automatic retry; failures visible in the dead-letter queue; load spread over hours.
- Cons: a company's report must fit inside one 15-minute run; "01:00" can be late by up to an hour plus queue time.
- **Portability: Adaptable** (any cron trigger and queue).

## Fitness criteria
1. The scheduler fires hourly; no job iterates over all companies in one invocation.
2. Report job keys are `company_id + local_date`; running a job twice produces one report and one email (tested).
3. The dead-letter queue has an alarm at one or more messages, and report queries use a read-only role with a statement timeout of at most 10 minutes.

## Revisit when
- Any company's report takes more than 8 minutes: chunk the job, or move report execution to a scheduled container task.
- Reports need to be near real time, or have dependencies between steps (consider a workflow service).
