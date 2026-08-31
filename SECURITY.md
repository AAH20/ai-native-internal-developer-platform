# Security policy

Report suspected vulnerabilities privately through GitHub security advisories. Do not commit OIDC keys, database credentials, cloud credentials, customer data or production telemetry.

Production mode refuses SQLite, disabled authentication and automatic schema mutation. Runtime secrets must be injected from an external secret system. The included Kubernetes secret reference is intentionally unresolved.
