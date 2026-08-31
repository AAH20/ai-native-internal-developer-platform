CREATE TABLE IF NOT EXISTS service_records (
    id VARCHAR(36) PRIMARY KEY,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(63) NOT NULL UNIQUE,
    owner VARCHAR(128) NOT NULL,
    service_type VARCHAR(32) NOT NULL,
    runtime VARCHAR(32) NOT NULL,
    data_classification VARCHAR(32) NOT NULL,
    availability_target DOUBLE PRECISION NOT NULL,
    monthly_budget_usd DOUBLE PRECISION NOT NULL,
    region VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    plan_json TEXT NOT NULL,
    receipt_sha256 VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_service_records_owner ON service_records(owner);
CREATE INDEX IF NOT EXISTS ix_service_records_created_at ON service_records(created_at DESC);
