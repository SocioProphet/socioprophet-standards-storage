# Access Control — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Identity Team + Platform DBA Team
- Standard references: NIST SP 800-53 AC-2, AC-3, AC-6, IA-2, IA-5, FIPS 140-2/140-3

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL](#postgresql)
3. [MongoDB](#mongodb)
4. [Elasticsearch / OpenSearch](#elasticsearch--opensearch)
5. [Redis](#redis)
6. [MinIO](#minio)
7. [RocksDB](#rocksdb)
8. [OIDC Integration](#oidc-integration)
9. [MFA Requirements](#mfa-requirements)
10. [Least Privilege Principles](#least-privilege-principles)
11. [Service Account Management](#service-account-management)
12. [NIST 800-53 Control Compliance](#nist-800-53-control-compliance)

---

## Overview

Access control for the data layer enforces the principle of least privilege through native database RBAC mechanisms, federated identity via OIDC, and multi-factor authentication for all privileged operations. No database user or service account may hold permissions beyond those required for its explicit, documented function.

### Access Control Hierarchy

```
OIDC Identity Provider (Keycloak / Dex)
        │
        ▼
HashiCorp Vault (secrets + dynamic credentials)
        │
        ├── PostgreSQL roles
        ├── MongoDB roles
        ├── Elasticsearch API keys
        ├── Redis ACL users
        ├── MinIO IAM policies
        └── RocksDB application roles
```

### Standard Role Tiers

Every data layer system implements the following role tiers, mapped to native database roles:

| Tier | Description | Typical Permissions |
|---|---|---|
| `readonly` | Read-only access to non-sensitive data | SELECT only; no DML |
| `readwrite` | Standard application access | SELECT, INSERT, UPDATE on designated tables/collections |
| `privileged_write` | Bulk operations, batch jobs | All DML; no DDL; no GRANT |
| `schema_owner` | Schema migrations (CI/CD only) | DDL; no data access in production |
| `replication` | Replication stream access | REPLICATION role; no data query |
| `backup` | Backup operations | SELECT (for dump), SUPERUSER restricted to backup tool |
| `monitoring` | Observability | Specific system catalog reads; no data access |
| `admin` | Operator access (break-glass) | Full access; requires MFA + PAM approval |

---

## PostgreSQL

### Role Hierarchy

```sql
-- Base roles (no login)
CREATE ROLE socioprophet_readonly NOLOGIN;
CREATE ROLE socioprophet_readwrite NOLOGIN;
CREATE ROLE socioprophet_privileged_write NOLOGIN;
CREATE ROLE socioprophet_schema_owner NOLOGIN;

-- Grant permissions to base roles
GRANT USAGE ON SCHEMA public TO socioprophet_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO socioprophet_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO socioprophet_readonly;

GRANT socioprophet_readonly TO socioprophet_readwrite;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO socioprophet_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT INSERT, UPDATE, DELETE ON TABLES TO socioprophet_readwrite;

GRANT USAGE, UPDATE ON ALL SEQUENCES IN SCHEMA public TO socioprophet_readwrite;

GRANT socioprophet_readwrite TO socioprophet_privileged_write;

-- Service account users (login roles)
CREATE ROLE api_service LOGIN PASSWORD NULL;  -- password set via Vault dynamic credentials
GRANT socioprophet_readwrite TO api_service;

CREATE ROLE worker_service LOGIN PASSWORD NULL;
GRANT socioprophet_readwrite TO worker_service;

CREATE ROLE monitoring_agent LOGIN PASSWORD NULL;
GRANT pg_monitor TO monitoring_agent;  -- built-in PostgreSQL 10+ monitoring role

CREATE ROLE backup_agent LOGIN PASSWORD NULL REPLICATION;
GRANT socioprophet_readonly TO backup_agent;
```

### Row-Level Security

For multi-tenant data, row-level security (RLS) enforces tenant isolation at the database level:

```sql
-- Enable RLS on the incidents table
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents FORCE ROW LEVEL SECURITY;  -- applies to table owner too

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON incidents
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Monitoring bypass (monitoring agent sees aggregate, not row data)
CREATE POLICY monitoring_bypass ON incidents
  FOR SELECT
  TO monitoring_agent
  USING (false);  -- monitoring agent sees no rows directly
```

### pg_hba.conf Authentication

```conf
# pg_hba.conf
# All network connections require TLS and SCRAM-SHA-256
hostssl socioprophet    api_service       10.0.0.0/8    scram-sha-256 clientcert=verify-full
hostssl socioprophet    worker_service    10.0.0.0/8    scram-sha-256 clientcert=verify-full
hostssl socioprophet    monitoring_agent  10.0.0.0/8    scram-sha-256 clientcert=verify-full
hostssl replication     backup_agent      10.0.0.0/8    scram-sha-256 clientcert=verify-full

# Operator access — cert CN must map via pg_ident
hostssl all             all               10.0.0.0/8    scram-sha-256 clientcert=verify-full map=ops-map

# Reject all plaintext connections
hostnossl all           all               0.0.0.0/0     reject

# Local superuser (maintenance only; monitored)
local   all             postgres                        peer
```

### SCRAM-SHA-256 Password Configuration

```sql
-- Enforce SCRAM-SHA-256 for all password-based authentication
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();

-- Verify all users use SCRAM-SHA-256 (not MD5)
SELECT usename, passwd FROM pg_shadow
WHERE passwd NOT LIKE 'SCRAM-SHA-256$%' AND passwd IS NOT NULL;
-- This query must return zero rows in a compliant deployment
```

### Dynamic Credentials via Vault

```hcl
# Vault database secrets engine — PostgreSQL
resource "vault_database_secret_backend_role" "api_service" {
  backend = vault_database_secrets_engine.postgres.path
  name    = "api-service"
  db_name = vault_database_secrets_engine_connection.postgres.name
  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT socioprophet_readwrite TO \"{{name}}\";",
  ]
  revocation_statements = ["DROP ROLE IF EXISTS \"{{name}}\";"]
  default_ttl = "1h"
  max_ttl     = "4h"
}
```

---

## MongoDB

### Role-Based Access Control

```javascript
// Enable RBAC (required in mongod.conf)
// security.authorization: enabled

// Create custom roles for SocioProphet
db.createRole({
  role: "socioprophetReadWrite",
  privileges: [
    {
      resource: { db: "socioprophet", collection: "" },
      actions: ["find", "insert", "update", "delete", "listCollections"]
    }
  ],
  roles: []
});

db.createRole({
  role: "socioprophetReadOnly",
  privileges: [
    {
      resource: { db: "socioprophet", collection: "" },
      actions: ["find", "listCollections"]
    }
  ],
  roles: []
});

// Create service users
db.createUser({
  user: "api_service",
  pwd: passwordPrompt(),  // set via Vault; never inline
  roles: [{ role: "socioprophetReadWrite", db: "socioprophet" }],
  mechanisms: ["SCRAM-SHA-256"]
});
```

### Built-In Role Restrictions

The following MongoDB built-in roles are **prohibited** for application service accounts:

| Prohibited Role | Reason |
|---|---|
| `dbOwner` | Includes destructive administrative operations |
| `dbAdmin` | Schema modification; not appropriate for application accounts |
| `clusterAdmin` | Full cluster control; operator break-glass only |
| `root` | Full superuser; prohibited for any automated account |
| `userAdmin` | Can grant itself any privilege; prohibited |
| `userAdminAnyDatabase` | Cluster-wide user management; prohibited |

### LDAP Authorization

```yaml
# mongod.conf — LDAP authorization
security:
  authorization: enabled
  ldap:
    servers: "ldap.internal:636"
    transportSecurity: tls
    bind:
      method: simple
      saslMechanisms: "PLAIN"
      queryUser: "cn=mongo-bind,ou=service,dc=socioprophet,dc=internal"
      queryPassword: "__vault_managed__"
    userToDNMapping: >
      [
        {
          match: "(.+)",
          ldapQuery: "ou=users,dc=socioprophet,dc=internal??sub?(uid={0})"
        }
      ]
    authz:
      queryTemplate: >
        {USER}?memberOf?base
```

---

## Elasticsearch / OpenSearch

### Index-Level Permissions

```json
// Create a role with index-level permissions
PUT _security/role/socioprophet_app
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["incidents*", "search*"],
      "privileges": ["read", "write", "create_index"],
      "allow_restricted_indices": false
    },
    {
      "names": ["audit*"],
      "privileges": ["read"],
      "allow_restricted_indices": false
    }
  ]
}

// Readonly role
PUT _security/role/socioprophet_readonly
{
  "indices": [
    {
      "names": ["incidents*", "search*"],
      "privileges": ["read"]
    }
  ]
}
```

### Document-Level Security

```json
// Role with DLS — users only see documents from their tenant
PUT _security/role/socioprophet_tenant_a
{
  "indices": [
    {
      "names": ["incidents*"],
      "privileges": ["read"],
      "query": "{\"term\": {\"tenant_id\": \"tenant-a-uuid\"}}"
    }
  ]
}
```

### Field-Level Security

```json
// Hide PII fields from search role
PUT _security/role/socioprophet_search_user
{
  "indices": [
    {
      "names": ["incidents*"],
      "privileges": ["read"],
      "field_security": {
        "grant": ["id", "title", "status", "severity", "created_at"],
        "except": ["reporter_email", "reporter_phone", "internal_notes"]
      }
    }
  ]
}
```

### API Key Management

```bash
# Create a time-limited API key for a service
POST /_security/api_key
{
  "name": "socioprophet-api-service",
  "expiration": "30d",
  "role_descriptors": {
    "app_role": {
      "cluster": ["monitor"],
      "indices": [
        {
          "names": ["incidents*"],
          "privileges": ["read", "write", "create_index"]
        }
      ]
    }
  }
}

# Invalidate a compromised API key immediately
POST /_security/api_key/invalidate
{
  "name": "socioprophet-api-service"
}
```

---

## Redis

### ACL System Configuration

```conf
# redis.conf — ACL file path
aclfile /etc/redis/users.acl
```

```conf
# /etc/redis/users.acl

# Disable default user (no anonymous access)
user default off nopass nocommands nokeys

# API service — read and write to specific key patterns only
user api_service on >__vault_managed_password__ \
  allchannels \
  ~sessions:* ~cache:* ~queue:* \
  +get +set +del +expire +ttl +exists +hget +hset +hdel +hgetall \
  +lpush +rpop +llen +lrange \
  +publish +subscribe \
  -config -debug -replicaof -bgrewriteaof -bgsave -flushall -flushdb

# Worker service — queue operations only
user worker_service on >__vault_managed_password__ \
  allchannels \
  ~queue:* ~job:* \
  +lpush +rpop +llen +brpop +lrange +del +expire +exists

# Monitoring agent — info and metrics only
user monitoring_agent on >__vault_managed_password__ \
  nokeys \
  +info +ping +client|list +slowlog|get +memory|usage

# Backup agent — RDB persistence triggers only
user backup_agent on >__vault_managed_password__ \
  nokeys \
  +bgsave +lastsave +debug|sleep
```

### Command Restrictions

Dangerous commands must be renamed or disabled to prevent accidental or malicious data destruction:

```conf
# redis.conf — rename dangerous commands
rename-command FLUSHALL ""        # Disable completely
rename-command FLUSHDB  ""        # Disable completely
rename-command DEBUG    ""        # Disable completely
rename-command CONFIG   "__vault_managed_admin_command_CONFIG__"
rename-command SHUTDOWN "__vault_managed_admin_command_SHUTDOWN__"
rename-command REPLICAOF "__vault_managed_admin_command_REPLICAOF__"
```

---

## MinIO

### Policy-Based Access Control

```json
// IAM policy for API service — read/write to specific prefixes
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": [
        "arn:aws:s3:::socioprophet-artifacts/*",
        "arn:aws:s3:::socioprophet-artifacts-staging/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::socioprophet-artifacts"],
      "Condition": {
        "StringLike": { "s3:prefix": ["incidents/*", "reports/*"] }
      }
    }
  ]
}
```

### Bucket Policies for Sensitive Data

```json
// Bucket policy — deny all non-TLS access
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::socioprophet-restricted-data/*"],
      "Condition": {
        "Bool": { "aws:SecureTransport": "false" }
      }
    }
  ]
}
```

### User and Group Management

```bash
# Create MinIO service users via mc
mc admin user add myminio api_service $(vault read -field=secret secret/minio/api-service)
mc admin policy attach myminio api-service-policy --user api_service

# Create groups for role aggregation
mc admin group add myminio app-services api_service worker_service
mc admin policy attach myminio app-services-policy --group app-services

# List all users and their policies
mc admin user list myminio
mc admin policy list myminio
```

---

## RocksDB

RocksDB is an embedded library. Access control is enforced entirely at the application layer.

### Application-Level RBAC Requirements

Every service embedding RocksDB must implement:

1. **Caller identity verification:** Every read/write operation must be associated with a verified caller identity (service account or operator identity from the request context).
2. **Key-space partitioning:** Different callers must access different key prefixes, enforced by the application before calling RocksDB APIs.
3. **Operation logging:** Every operation must be logged to the audit trail (see `AUDIT-LOGGING.md`).

```python
# Application RBAC wrapper for RocksDB
class SecureRocksDB:
    ALLOWED_PREFIXES = {
        "api_service": [b"session:", b"cache:"],
        "worker_service": [b"job:", b"queue:"],
        "backup_agent": [],  # backup via checkpoint only; no key access
    }

    def get(self, key: bytes, caller: str) -> bytes:
        self._check_access(key, caller, "read")
        return self._db.get(key)

    def put(self, key: bytes, value: bytes, caller: str) -> None:
        self._check_access(key, caller, "write")
        self._audit.log("write", key_prefix=key[:16], caller=caller)
        self._db.put(key, value)

    def _check_access(self, key: bytes, caller: str, op: str):
        allowed = self.ALLOWED_PREFIXES.get(caller, [])
        if not any(key.startswith(p) for p in allowed):
            self._audit.log("access_denied", key_prefix=key[:16], caller=caller, op=op)
            raise PermissionError(f"Caller {caller} not permitted to {op} key with this prefix")
```

---

## OIDC Integration

All data layer systems must integrate with the centralized OIDC provider for authentication where technically supported.

### OIDC Integration Status

| System | OIDC Support | Integration Method | Status |
|---|---|---|---|
| PostgreSQL | Via Vault OIDC auth + dynamic credentials | Vault database secrets engine | 🔄 Q3 2026 |
| MongoDB | Native OIDC (MongoDB 7.0+ Enterprise) | `security.oidc` in mongod.conf | 🔄 Q3 2026 |
| Elasticsearch | Native OIDC via X-Pack | `xpack.security.authc.realms.oidc` | ✅ Implemented |
| Redis | Not natively supported; bridge via Vault | Vault agent + ACL credential injection | ❌ Q4 2026 |
| MinIO | Native OIDC | `MINIO_IDENTITY_OPENID_*` environment variables | 🔄 Q3 2026 |
| RocksDB | Application layer (pass-through from service OIDC) | Service authenticates; passes identity to RocksDB wrapper | N/A |

### MinIO OIDC Configuration

```bash
# MinIO OIDC environment variables
MINIO_IDENTITY_OPENID_CONFIG_URL=https://keycloak.internal/realms/socioprophet/.well-known/openid-configuration
MINIO_IDENTITY_OPENID_CLIENT_ID=minio
MINIO_IDENTITY_OPENID_CLIENT_SECRET=__vault_managed__
MINIO_IDENTITY_OPENID_CLAIM_NAME=policy
MINIO_IDENTITY_OPENID_DISPLAY_NAME=SocioProphet SSO
MINIO_IDENTITY_OPENID_SCOPES=openid,profile,email
MINIO_IDENTITY_OPENID_REDIRECT_URI=https://minio.internal/oauth_callback
```

### Elasticsearch OIDC Configuration

```yaml
# elasticsearch.yml
xpack.security.authc.realms.oidc.socioprophet-oidc:
  order: 1
  rp.client_id: "elasticsearch"
  rp.response_type: "code"
  rp.redirect_uri: "https://es.internal:9200/api/security/oidc/callback"
  op.issuer: "https://keycloak.internal/realms/socioprophet"
  op.authorization_endpoint: "https://keycloak.internal/realms/socioprophet/protocol/openid-connect/auth"
  op.token_endpoint: "https://keycloak.internal/realms/socioprophet/protocol/openid-connect/token"
  op.jwkset_path: "oidc/jwkset.json"
  claims.principal: sub
  claims.groups: roles
```

---

## MFA Requirements

Multi-factor authentication is required for all privileged database operations.

### Privileged Operations Requiring MFA

| Operation | Systems | MFA Method |
|---|---|---|
| Direct operator database login | All | TOTP (FIDO2 preferred) via Keycloak |
| Schema migration execution | PostgreSQL, MongoDB | Vault token + TOTP |
| Key rotation initiation | All | Vault + MFA policy on Vault login |
| User/role creation or deletion | All | Vault + MFA policy |
| Backup restoration | All | Vault + TOTP + manager approval workflow |
| Break-glass admin access | All | Vault emergency MFA + CISO notification |
| RLS / ACL policy changes | PostgreSQL, Redis | Vault + TOTP |
| WORM override / audit log access | MinIO, OpenSearch | Vault emergency MFA + dual approval |

### Vault MFA Policy

```hcl
# Vault MFA configuration — TOTP required for privileged operations
resource "vault_mfa_totp" "admin_mfa" {
  name         = "admin-totp"
  issuer       = "SocioProphet Vault"
  period       = 30
  key_size     = 20
  qr_size      = 200
  algorithm    = "SHA256"
  digits       = 6
}

resource "vault_mfa_login_enforcement" "admin_enforcement" {
  name            = "admin-mfa-enforcement"
  mfa_method_ids  = [vault_mfa_totp.admin_mfa.id]
  auth_method_accessors = [vault_auth_backend.userpass.accessor]
  identity_group_ids = [vault_identity_group.db_admins.id]
}
```

---

## Least Privilege Principles

### Minimal Grant Checklist

Before granting any database permission, validate:

- [ ] The permission is required for a documented, current use case.
- [ ] A less privileged alternative (e.g., a view, stored procedure, or restricted role) cannot satisfy the requirement.
- [ ] The permission is scoped to the minimum namespace (specific table/collection, not all tables).
- [ ] The permission has a defined expiry or review date (for temporary grants).
- [ ] The grant is recorded in the service's access control registry.

### Prohibited Grants

The following are unconditionally prohibited for all service accounts:

| Permission | Systems | Alternative |
|---|---|---|
| `SUPERUSER` | PostgreSQL | Use specific system catalog roles + `pg_monitor` |
| `CREATEROLE` | PostgreSQL | Role management via Vault/DBA team only |
| `root` role | MongoDB | Use custom least-privilege role |
| `cluster:*` | Elasticsearch | Use `monitor` + specific index privileges |
| `FLUSHALL` / `FLUSHDB` | Redis | Rename to undiscoverable name; admin-only |
| `s3:*` wildcard | MinIO | Enumerate specific required actions |
| `admin` policy | MinIO | Use `readwrite` with path restrictions |

---

## Service Account Management

### Lifecycle Policy

| Phase | Trigger | Required Action |
|---|---|---|
| Creation | New service deployment | Create via Vault dynamic credentials; document in access registry |
| Credential rotation | 30 days (service accounts), 24 hours (short-lived tokens) | Automated via Vault lease renewal |
| Permission review | Quarterly | Compare granted permissions to documented requirements |
| Suspension | Service decommissioned or compromised | Revoke Vault lease; disable database user; audit access history |
| Deletion | 30 days post-suspension | Delete database user; purge Vault role |

### Credential Storage

Service account credentials must never be stored in:

- Source code or configuration files in version control
- Container image layers
- Environment variables set at build time
- CI/CD pipeline secrets (use Vault agent sidecar instead)

All credentials must be retrieved at runtime from HashiCorp Vault via:

1. Kubernetes service account token authentication to Vault (preferred for Kubernetes deployments)
2. AppRole authentication with secret ID injected via Vault Agent (non-Kubernetes deployments)

---

## NIST 800-53 Control Compliance

| Control | Title | Implementation |
|---|---|---|
| AC-2 | Account Management | Service account lifecycle policy; Vault dynamic credentials; quarterly review |
| AC-3 | Access Enforcement | RBAC on all systems; RLS in PostgreSQL; DLS in Elasticsearch; ACL in Redis |
| AC-6 | Least Privilege | Minimal grant checklist; prohibited permissions list; Vault dynamic credentials |
| AC-17 | Remote Access | mTLS required for all remote database connections; VPN not a substitute |
| IA-2 | Identification and Authentication | SCRAM-SHA-256 in PostgreSQL; x.509 mTLS; OIDC federation |
| IA-5 | Authenticator Management | Vault-managed credentials; 30-day rotation; SCRAM-SHA-256 only |
| IA-8 | Non-Org User Identification | OIDC federation for external identity providers |
| IA-11 | Re-Authentication | Token TTL max 4h; re-authentication required for privileged operations (MFA) |
