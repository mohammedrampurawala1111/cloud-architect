# ADR-0004: Keep 13 months of history in S3 Parquet, queried with Athena and rollups

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
About 67 B rows over 13 months. Dashboards need fine resolution for recent data and coarse resolution for old data, for up to about 50 concurrent users (assumed).

## Decision drivers
- Cost and simplicity at 67 B rows.
- Team-fit: no database to size, patch or restore.
- Portability: open data format.

## Options considered
- **S3 Parquet plus Athena with scheduled rollups.**
- **Aurora PostgreSQL or RDS:** 67 B raw rows does not fit comfortably; rollups alone would (about 190 M hourly rows) but drill-down would be lost.
- **Self-hosted TimescaleDB or ClickHouse:** fast, but a self-hosted database is weight 4.
- **Amazon Timestream:** not selected; product availability for new customers and its direction need checking (verify).

## Decision
We chose S3 plus Athena because it stores 13 months for a few hundred dollars a month, needs no capacity management, and keeps data in an open format. Firehose writes Parquet partitioned by date and hour. Scheduled Step Functions workflows build 5-minute, hourly and daily rollup tables; dashboards read rollups for ranges over 24 h and raw data only for drill-down. An S3 lifecycle rule deletes raw data after 400 days.

## Consequences
- Dashboards see raw data 1-2 minutes late (Firehose buffering); rollups lag by up to 15 minutes.
- Query latency is seconds, not milliseconds; Athena concurrency quotas are the first limit likely to bind (verify quota).
- Portability: **Portable** (S3 Parquet), **Adaptable** (Athena; Trino or other engines can read the same files).

## Fitness criteria
1. Raw and rollup tables are Parquet in S3 in ap-southeast-2, with a lifecycle rule expiring raw objects at 400 days.
2. Dashboard queries for ranges over 24 h read rollup tables only (check: no Grafana panel query references the raw table for such ranges).
3. Dashboard p95 query time is under 10 s on rollups (Athena query metrics).

## Revisit when
- More than about 50 concurrent dashboard users, or p95 above 10 s for two weeks: add a serving store (for example Aurora PostgreSQL for hourly and daily rollups).
