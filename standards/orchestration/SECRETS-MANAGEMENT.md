# Secrets Management — HashiCorp Vault HA Standards

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Security Engineering / Platform Engineering
- Applies to: All SocioProphet Vault clusters (production, DR, staging)

---

## Table of Contents

1. [Vault HA Configuration](#vault-ha-configuration)
2. [OIDC Authentication Method](#oidc-authentication-method)
3. [Kubernetes Authentication Method](#kubernetes-authentication-method)
4. [Secret Engines](#secret-engines)
5. [Dynamic Credentials for Database Access](#dynamic-credentials-for-database-access)
6. [Secret Rotation Schedules](#secret-rotation-schedules)
7. [Disaster Recovery and Backup](#disaster-recovery-and-backup)
8. [Audit Device Configuration](#audit-device-configuration)
9. [Vault Agent Sidecar Injection](#vault-agent-sidecar-injection)
10. [Break-Glass Emergency Procedures](#break-glass-emergency-procedures)

---

## Vault HA Configuration

The SocioProphet platform runs HashiCorp Vault Enterprise FIPS 140-2 Edition. The FIPS edition uses a FIPS 140-2 validated cryptographic module (BoringCrypto) for all seal/unseal operations, token generation, and secret encryption.

### Cluster Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                  Vault Primary Cluster (us-east-1)             │
│                                                                  │
│  vault-0 (Active)   vault-1 (Standby)   vault-2 (Standby)      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │ Raft Leader  │   │ Raft Follower│   │ Raft Follower│        │
│  │ 10.0.1.10    │   │ 10.0.1.11    │   │ 10.0.1.12    │        │
│  └──────────────┘   └──────────────┘   └──────────────┘        │
│  Raft Quorum: 2 of 3 required for writes                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │ DR Replication (async)
┌──────────────────────────▼──────────────────────────────────────┐
│                  Vault DR Cluster (us-west-2)                   │
│  vault-dr-0 (DR Secondary)  vault-dr-1  vault-dr-2              │
└─────────────────────────────────────────────────────────────────┘
```

### Vault Configuration (vault.hcl)

```hcl
ui = false
disable_mlock = false
log_level = "info"
log_format = "json"

api_addr = "https://vault.socioprophet.internal:8200"
cluster_addr = "https://vault-0.vault-internal.vault.svc.cluster.local:8201"

storage "raft" {
  path    = "/vault/data"
  node_id = "vault-0"

  retry_join {
    auto_join             = "provider=k8s label_selector=\"app=vault,component=server\" namespace=\"vault\""
    auto_join_scheme      = "https"
    auto_join_port        = 8201
    leader_tls_servername = "vault-internal.vault.svc.cluster.local"
    leader_ca_cert_file   = "/vault/tls/ca.crt"
    leader_client_cert_file = "/vault/tls/tls.crt"
    leader_client_key_file  = "/vault/tls/tls.key"
  }
}

listener "tcp" {
  address            = "0.0.0.0:8200"
  tls_cert_file      = "/vault/tls/tls.crt"
  tls_key_file       = "/vault/tls/tls.key"
  tls_client_ca_file = "/vault/tls/ca.crt"
  tls_min_version    = "tls12"
  tls_cipher_suites  = "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
}

seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"
  # AWS KMS key must be AES-256 (FIPS-approved)
}

telemetry {
  prometheus_retention_time = "30s"
  disable_hostname           = true
}
```

### Auto-Unseal

Vault is configured to auto-unseal using AWS KMS (AES-256 key). The KMS key policy permits only the Vault EC2 instance role and the Security Engineering break-glass role to use the key.

---

## OIDC Authentication Method

```bash
# Enable OIDC auth method
vault auth enable oidc

# Configure OIDC
vault write auth/oidc/config \
  oidc_discovery_url="https://auth.socioprophet.internal/oidc" \
  oidc_client_id="vault" \
  oidc_client_secret="$(vault kv get -field=client_secret kv/v2/vault/oidc-client)" \
  default_role="developer"

# Create a role for platform engineers
vault write auth/oidc/role/platform-engineer \
  bound_audiences="vault" \
  allowed_redirect_uris="https://vault.socioprophet.internal:8250/oidc/callback" \
  groups_claim="groups" \
  token_policies="platform-engineer-policy" \
  token_ttl="8h" \
  token_max_ttl="24h"
```

### OIDC Group Mappings

| OIDC Group | Vault Policy | Access Scope |
|---|---|---|
| `oidc:platform-engineers` | `platform-engineer-policy` | All paths except break-glass |
| `oidc:security-engineers` | `security-engineer-policy` | All paths including PKI root |
| `oidc:developers` | `developer-policy` | `kv/v2/dev/*` only |
| `oidc:ci-cd` | `cicd-policy` | Read `kv/v2/ci/*`; write `kv/v2/ci/artifacts/*` |

---

## Kubernetes Authentication Method

```bash
# Enable Kubernetes auth
vault auth enable kubernetes

# Configure with in-cluster service account
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc.cluster.local:443" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  issuer="https://kubernetes.socioprophet.internal"

# Create a role for the socioprophet-prod service accounts
vault write auth/kubernetes/role/socioprophet-prod \
  bound_service_account_names="socioprophet-workload,external-secrets-sa,vault-agent-sa" \
  bound_service_account_namespaces="socioprophet-prod" \
  token_policies="socioprophet-prod-policy" \
  token_ttl="1h" \
  token_max_ttl="4h"
```

### Per-Namespace Roles

Each Kubernetes namespace has a dedicated Vault role with the minimum required policy. Roles are named `kubernetes-<namespace>`.

---

## Secret Engines

### KV v2 Engine

```bash
vault secrets enable -path=socioprophet kv-v2
vault secrets tune -default-lease-ttl=24h -max-lease-ttl=768h socioprophet/
```

### PKI Engine

```bash
# Enable PKI engine for internal CA
vault secrets enable -path=pki pki
vault secrets tune -max-lease-ttl=87600h pki/

# Generate root CA (ECDSA P-384)
vault write pki/root/generate/internal \
  common_name="SocioProphet Internal CA" \
  key_type="ec" \
  key_bits=384 \
  ttl=87600h

# Enable intermediate CA for cert-manager
vault secrets enable -path=pki-intermediate pki
vault write pki-intermediate/intermediate/generate/internal \
  common_name="SocioProphet Intermediate CA" \
  key_type="ec" \
  key_bits=256
```

### Transit Engine

```bash
vault secrets enable transit

# Create named keys for specific purposes
vault write transit/keys/etcd-encryption type=aes256-gcm96
vault write transit/keys/cosign-platform-signing-key type=ecdsa-p256
vault write transit/keys/audit-log-signing type=ecdsa-p256
```

### Database Engine

```bash
vault secrets enable database

# PostgreSQL configuration
vault write database/config/socioprophet-postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="app-read-only,app-read-write" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.socioprophet-data.svc.cluster.local:5432/socioprophet?sslmode=verify-full&sslrootcert=/vault/tls/ca.crt" \
  username="vault-root" \
  password="$(vault kv get -field=password kv/v2/vault/db-root)"
```

---

## Dynamic Credentials for Database Access

### PostgreSQL Roles

```bash
vault write database/roles/app-read-write \
  db_name=socioprophet-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT app_read_write TO \"{{name}}\";" \
  revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
  default_ttl=1h \
  max_ttl=4h

vault write database/roles/app-read-only \
  db_name=socioprophet-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT app_read_only TO \"{{name}}\";" \
  revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
  default_ttl=4h \
  max_ttl=24h
```

### MongoDB Dynamic Credentials

```bash
vault write database/config/socioprophet-mongodb \
  plugin_name=mongodb-database-plugin \
  allowed_roles="mongo-app-rw" \
  connection_url="mongodb://{{username}}:{{password}}@mongodb.socioprophet-data.svc.cluster.local:27017/admin?tls=true" \
  username="vault-mongo-root" \
  password="$(vault kv get -field=password kv/v2/vault/mongodb-root)"

vault write database/roles/mongo-app-rw \
  db_name=socioprophet-mongodb \
  creation_statements='{"db": "socioprophet", "roles": [{"role": "readWrite"}]}' \
  default_ttl=1h \
  max_ttl=4h
```

---

## Secret Rotation Schedules

| Secret Type | Maximum Lifetime | Rotation Method | Owner |
|---|---|---|---|
| Dynamic DB credentials (PostgreSQL) | 4 hours | Automatic (Vault TTL) | Vault |
| Dynamic DB credentials (MongoDB) | 4 hours | Automatic (Vault TTL) | Vault |
| KV static secrets (API keys) | 90 days | `vault kv put` + ESO refresh | Security Eng |
| Vault root token | Used once, then revoked | Manual (break-glass only) | Security Eng |
| Vault unseal key (KMS) | 1 year | AWS KMS key rotation | Security Eng |
| PKI intermediate CA cert | 1 year | cert-manager renewal | Platform Eng |
| Workload SVID certificates | 24 hours | Automatic (Istio CA) | Istio |
| Registry robot account tokens | 365 days | Manual (Harbor UI) | DevSecOps |

---

## Disaster Recovery and Backup

### Vault DR Replication

```bash
# On primary: enable DR replication
vault write -f sys/replication/dr/primary/enable

# Generate secondary activation token
vault write sys/replication/dr/primary/secondary-token id=dr-us-west-2

# On DR secondary: enable and activate
vault write sys/replication/dr/secondary/enable \
  token=<secondary-token> \
  primary_api_addr=https://vault.socioprophet.internal:8200
```

DR replication is asynchronous with a lag target of < 30 seconds. The DR secondary cluster is read-only unless promoted during a failover event.

### Raft Snapshot Backup

```bash
# Take a Raft snapshot (run every 4 hours via CronJob)
vault operator raft snapshot save /backup/vault-snapshot-$(date +%Y%m%d%H%M%S).snap

# Upload to S3 (encrypted with Vault-managed KMS key)
aws s3 cp /backup/vault-snapshot-*.snap \
  s3://socioprophet-vault-backups/$(date +%Y/%m/%d)/ \
  --sse aws:kms \
  --sse-kms-key-id arn:aws:kms:us-east-1:ACCOUNT:key/BACKUP-KEY-ID
```

### DR Failover Procedure

1. Confirm primary cluster is unreachable (not just a network partition).
2. Obtain quorum approval from two Security Engineering principals.
3. Promote DR secondary: `vault write -f sys/replication/dr/secondary/promote dr_operation_token=<token>`.
4. Update DNS: point `vault.socioprophet.internal` to the new primary.
5. Notify all teams and open an incident ticket.
6. After recovery: re-establish DR replication from the recovered primary to the promoted secondary.

---

## Audit Device Configuration

```bash
# File audit device (primary — for local log shipping)
vault audit enable file \
  file_path=/vault/audit/vault-audit.log \
  format=json \
  log_raw=false \
  hmac_accessor=true

# Syslog audit device (secondary — for SIEM integration)
vault audit enable syslog \
  facility=AUTH \
  tag=vault \
  format=json \
  log_raw=false
```

All audit log entries are HMAC-signed (HMAC-SHA-256 with the Vault audit HMAC key). The `log_raw=false` setting ensures that secret values are never written to the audit log; only HMACs of values are recorded.

Audit logs are shipped to OpenSearch via the Vector pipeline described in [AUDIT-OBSERVABILITY.md](./AUDIT-OBSERVABILITY.md) and retained for 7 years.

---

## Vault Agent Sidecar Injection

```yaml
# Annotate a Deployment to inject Vault Agent
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graph-service
  namespace: socioprophet-prod
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "socioprophet-prod"
        vault.hashicorp.com/agent-inject-secret-db-credentials: "socioprophet/data/database"
        vault.hashicorp.com/agent-inject-template-db-credentials: |
          {{- with secret "socioprophet/data/database" -}}
          DB_PASSWORD={{ .Data.data.password }}
          DB_USERNAME={{ .Data.data.username }}
          {{- end }}
        vault.hashicorp.com/tls-skip-verify: "false"
        vault.hashicorp.com/ca-cert: "/vault/tls/ca.crt"
        vault.hashicorp.com/agent-pre-populate-only: "false"
```

The injected secret is written to an in-memory tmpfs volume at `/vault/secrets/`. It is never written to disk or exposed as an environment variable.

---

## Break-Glass Emergency Procedures

Break-glass access to Vault is granted only during declared incidents where normal OIDC authentication is unavailable. The procedure requires dual approval and is fully audited.

### Procedure

1. Open an emergency incident ticket (P0).
2. Contact the Security Engineering on-call (PagerDuty) and a second Security Engineering principal.
3. Both principals retrieve their Vault recovery key shares from their hardware security tokens (YubiKey).
4. On a trusted workstation (not a shared server): `vault operator generate-root -init` and proceed through the key share reconstruction.
5. Use the generated root token to perform the emergency operation.
6. Immediately revoke the root token after use: `vault token revoke <root-token>`.
7. Document all commands executed with timestamps in the incident ticket.
8. Rotate any credentials that may have been visible during the emergency session.

### Root Token Policy

The initial Vault root token generated at cluster initialization is revoked immediately after the cluster is sealed and unsealed successfully for the first time. No standing root token exists in the production Vault cluster.
