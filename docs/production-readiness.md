# Production-readiness contract

Production-ready means the software contains the necessary controls and has passed an environment-specific operational acceptance process. This repository provides the former; it does not claim the latter without a retained deployment record.

## Implemented controls

- OIDC bearer-token validation with issuer, audience, signature and role checks
- production startup rejection for SQLite, disabled authentication or automatic schema mutation
- PostgreSQL schema and explicit migration artifact
- idempotent service creation backed by a unique database constraint
- deterministic plan receipts
- budget rejection before service persistence
- liveness, readiness and startup probes
- Prometheus metrics
- non-root, read-only container
- resource limits, horizontal scaling and disruption budget
- default-deny network policy
- three-replica rolling deployment with topology spreading
- GitOps application with self-healing and retained revision history

## Required environment acceptance

- Configure Microsoft Entra ID or another OIDC issuer and test key rotation.
- Use managed PostgreSQL with backups, point-in-time recovery and zone redundancy.
- Apply migrations through a dedicated release job.
- Use external secret synchronization; never create the runtime secret in Git.
- Restrict ingress, database egress and DNS according to the actual cluster topology.
- Sign images, generate SBOMs and enforce admission verification.
- Load-test API and database saturation behavior.
- Perform pod, node, zone and database failover drills.
- Validate backup restoration and migration rollback.
- Establish on-call ownership, SLOs and incident response.

No repository can honestly claim production acceptance without these organization-specific tests.
