# SLO and operational runbook

## Service-level objectives

- Availability: 99.95% successful control-plane requests per rolling 30 days
- Latency: p95 service-intent compilation below 500 ms, excluding external provider calls
- Correctness: zero duplicate service records for the same idempotency key
- Durability: committed service intent survives process and pod restart
- Recovery: API RTO 30 minutes; PostgreSQL RPO defined by managed backup configuration

## Alerts

- Readiness failure for two consecutive minutes
- Error-budget burn greater than 14.4x over one hour or 6x over six hours
- Database connection saturation
- Rejected authentication spike
- Budget-gate rejection anomaly
- Idempotency-constraint conflict anomaly
- p95 latency and request-error threshold breach

## First-response sequence

1. Confirm blast radius and recent GitOps revision.
2. Inspect readiness, database connectivity and OIDC verification failures.
3. Freeze template promotion while preserving read access.
4. Roll back the application revision if the database schema is backward compatible.
5. Restore PostgreSQL only through the documented managed-service recovery process.
6. Preserve traces, audit events and receipts for the incident review.
