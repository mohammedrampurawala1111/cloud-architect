# ADR-0005: Produce the finance export as a scheduled Athena job writing to S3

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Finance needs a daily file. Assumed content: per customer and device, per day, reading counts, uptime and billable units; no raw readings. Assumed ready by 06:00 Sydney time. Format and delivery channel need finance's confirmation.

## Decision drivers
- Reuse existing data (S3 Parquet, Athena); no new service.
- Reproducibility: finance can rerun a day and get the same file.
- Team-fit: managed scheduler and workflow.

## Options considered
- **EventBridge Scheduler, Step Functions, Athena, CSV into a dedicated export bucket.**
- **Lambda that queries and emails the file:** simple, but harder to rerun and audit.
- **Push to finance's own system or SFTP:** adds a managed transfer service; wait for finance's requirements.

## Decision
We chose a scheduled workflow at 02:00 Australia/Sydney (the scheduler handles daylight saving) that runs an Athena query over the previous local day's rollups, writes `export/date=YYYY-MM-DD/usage.csv` to a dedicated bucket, and sends a notification. The job is idempotent (same key overwritten) and takes the date as a parameter for reruns. Finance gets read access through a role or presigned link.

## Consequences
- The export derives from rollups, so a daily reconciliation compares its counts with the raw table.
- Pushing to a finance system, if needed, is an extension.
- Portability: **Adaptable** (SQL, cron and object storage).

## Fitness criteria
1. A file for each Sydney calendar day exists in the export bucket by 06:00 Sydney time (alarm if missing).
2. The workflow accepts a date parameter and rerunning it produces an identical file.
3. Daily reading counts in the export match the raw table within 0.1% (reconciliation recorded as a metric).

## Revisit when
- Finance requires a push to their system, another format, or intraday delivery.
