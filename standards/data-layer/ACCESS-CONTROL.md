# Access Control Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines authentication, authorization, and access-review requirements for all
data-layer systems, satisfying NIST SP 800-53 AC-2, AC-3, IA-2, IA-5, and IA-8.

## 2. Per-Database Authentication

### 2.1 PostgreSQL

- `pg_hba.conf` MUST use `scram-sha-256` for all password-based authentication.
  `md5` authentication MUST be disabled.
- Service accounts MUST use certificate authentication (`cert` method) where possible.
- Superuser login from remote hosts MUST be disabled (`pg_hba.conf` restricts superusers to
  `local` socket or explicit IP whitelist).

### 2.2 MongoDB

- Authentication MUST be enabled (`security.authorization: enabled`).
- Supported mechanisms: `SCRAM-SHA-256` (default), LDAP (enterprise), Kerberos (enterprise),
  or X.509 certificate authentication.
- `SCRAM-SHA-1` MUST be disabled (`authenticationMechanisms: SCRAM-SHA-256`).

```yaml
# mongod.conf excerpt
security:
  authorization: enabled
setParameter:
  authenticationMechanisms: SCRAM-SHA-256
```

### 2.3 Elasticsearch

- Built-in user passwords MUST be set via `elasticsearch-setup-passwords` or the
  Security API before first use.
- Supported mechanisms: API keys, JWT, SAML, OIDC (preferred for human users).
- Native realm passwords MUST satisfy the complexity policy in §4.

### 2.4 Redis

- ACL MUST be enabled (Redis 6.0+) with `aclfile /etc/redis/users.acl`.
- The default `requirepass` MUST use a password derived via **PBKDF2-HMAC-SHA256** (RFC 2898)
  with a minimum of 310,000 iterations and a 128-bit salt.
- The default user MUST be disabled: `user default off`.

```
# users.acl excerpt
user default off
user appservice on >StrongGeneratedPassword123! ~app:* &* +@read +@write -@dangerous
```

### 2.5 MinIO

- IAM policies MUST follow least-privilege: each service account gets only the S3 actions and
  bucket prefixes it requires.
- OIDC federation MUST be configured for human users; static access keys MUST NOT be issued to
  human operators.

## 3. Multi-Factor Authentication

| System | MFA Applicability |
|---|---|
| Elasticsearch | OIDC + MFA enforced at identity provider |
| MinIO | OIDC + MFA enforced at identity provider |
| PostgreSQL | Certificate auth acts as second factor for service accounts |
| MongoDB | Kerberos / LDAP with MFA enforced at IdP for privileged users |
| Redis | Not natively supported; restrict to service accounts only |

Human operators accessing any data system MUST authenticate via an OIDC-capable identity
provider with MFA enabled.

## 4. Password Policy (NIST SP 800-63B)

- Minimum length: 15 characters.
- Maximum length: 128 characters (do not truncate).
- No mandatory complexity rules beyond length (NIST 800-63B §5.1.1); allow any printable ASCII.
- Passwords MUST be checked against known-compromised password lists before acceptance.
- Rotation: passwords MUST be rotated when compromised or at key-rotation intervals;
  scheduled rotation without indication of compromise is discouraged per 800-63B.
- Account lockout: accounts MUST lock after 10 consecutive failed attempts; unlock requires
  administrator or MFA re-authentication.

## 5. Least-Privilege Role Configuration

### 5.1 General Principles

- Every service account MUST have the minimum permissions required for its function.
- Separation of duties MUST be enforced: the same principal MUST NOT be able to both write
  data and delete audit logs.
- DBA / admin accounts MUST be separate from application service accounts.

### 5.2 Per-System RBAC

#### PostgreSQL

```sql
-- Read-only service account
CREATE ROLE svc_reader LOGIN PASSWORD '...'
  NOSUPERUSER NOCREATEDB NOCREATEROLE;
GRANT CONNECT ON DATABASE mydb TO svc_reader;
GRANT USAGE ON SCHEMA public TO svc_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO svc_reader;
```

#### MongoDB

```javascript
// Application role — read/write own collection only
db.createRole({
  role: "appRole",
  privileges: [
    { resource: { db: "appdb", collection: "events" }, actions: ["find","insert","update"] }
  ],
  roles: []
});
```

#### Redis

- Use ACL categories (`+@read`, `+@write`) with key-pattern restrictions (`~prefix:*`).
- Disable `@dangerous` category for all non-admin users.

### 5.3 Service Account Management

- Service account credentials MUST be stored in the platform secrets manager (e.g., Vault).
- Credentials MUST never appear in source code, environment files committed to VCS, or
  container images.
- Service accounts MUST NOT be shared across services.

## 6. Access Review Procedures

- A full review of all database accounts and roles MUST be conducted **quarterly**.
- The review MUST:
  - Verify each account is still required.
  - Confirm privileges match current least-privilege requirements.
  - Identify and disable accounts inactive for more than 90 days.
  - Document privilege escalation rationale.
- Results MUST be recorded in the audit log and retained per [AUDIT-LOGGING.md](AUDIT-LOGGING.md).
