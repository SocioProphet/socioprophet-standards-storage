# Ray Ecosystem Governance

## Overview

This standard defines governance controls for all components of the Ray ecosystem deployed on the
SocioProphet platform: Ray Core, Ray Serve, Ray Tune, Ray Train, Ray Data, and Ray Workflows.
Ray is the designated distributed ML platform and its security posture directly affects all
training, tuning, and serving workloads.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Ray Core Security

### 1.1 Dashboard Access

- The Ray dashboard MUST be exposed only via an authenticated reverse proxy.
- Direct access to the Ray dashboard port MUST be blocked by NetworkPolicy.
- The proxy MUST enforce OIDC authentication and log all access events.

### 1.2 Object Store Encryption

- Data placed in the Ray plasma (object) store MUST be encrypted at rest with AES-256-GCM.
- The encryption key MUST be unique per job and provisioned from Vault at job start.

### 1.3 Centralised Log Forwarding

- Task and actor logs MUST be forwarded to the centralised logging system in real time.
- Logs MUST include: job ID, task/actor ID, worker node, timestamp, and log level.

### 1.4 Task Submission Audit Logging

- All task and actor submissions MUST generate an audit log entry containing: submitter identity,
  job ID, resource request, and timestamp.

### 1.5 Worker Isolation

- Workers MUST run in isolated containers or VMs with no shared filesystem access between jobs.
- A worker MUST NOT be reused across jobs without a fresh container/VM provisioned.

---

## 2. Ray Serve Deployment

### 2.1 Autoscaling

- Ray Serve replicas MUST autoscale based on request queue depth or CPU utilisation.
- Minimum and maximum replica counts MUST be set per deployment.
- Autoscale events (scale-up and scale-down) MUST be logged.

### 2.2 Rolling Deployments

- Model updates MUST be deployed using a rolling strategy (zero downtime).
- At no point MUST all replicas of a version be simultaneously replaced.
- Rolling update progress MUST be observable via the monitoring system.

### 2.3 Model Immutability

- A deployed model version MUST NOT be updated in-place (see
  [MODEL-SERVING-SECURITY.md](MODEL-SERVING-SECURITY.md) §4.1).
- Version changes require a new deployment with a new version tag.

### 2.4 Traffic Splitting for A/B Testing

- Traffic splitting configuration MUST be stored in the CK deployment record.
- Traffic weights MUST sum to 100% at all times.
- Changes to traffic weights MUST generate an audit log entry.

### 2.5 Metrics Export

- Request latency, error rate, and throughput MUST be exported to Prometheus.
- Metrics MUST be labelled with `model_name` and `model_version` dimensions.

---

## 3. Ray Tune Configuration

### 3.1 Frozen Search Spaces

- Hyperparameter search spaces MUST be declared in a version-controlled configuration file.
- Search spaces MUST NOT be modified after a tuning run has been initiated.
- The configuration file commit SHA MUST be stored in the tuning job provenance record.

### 3.2 Immutable Trial Results

- Once a trial completes, its configuration and result MUST be written to the CK backend as an
  immutable record.
- Corrections to trial records require creating a new superseding record with a reference to the
  original.

### 3.3 Search Algorithm Audit Log

- The search algorithm used (e.g. Bayesian optimisation, ASHA) and its configuration MUST be
  logged.

### 3.4 Early Stopping Rationale

- If early stopping is used, the stopping criterion (metric, threshold, patience) MUST be
  documented and stored in the tuning job record.

### 3.5 Best Trial Selection

- Best trial selection MUST be automated based on the primary metric defined at job submission.
- Manual overrides to the automated selection MUST be justified and recorded in the CK audit
  trail.

---

## 4. Ray Train Integration

### 4.1 Distributed Training Encryption

- See [TRAINING-PIPELINE-SECURITY.md](TRAINING-PIPELINE-SECURITY.md) §2.3 for per-worker
  encryption requirements.

### 4.2 Model Checkpointing

- Checkpoints MUST be written to encrypted storage (AES-256-GCM).
- Each checkpoint MUST include a SHA-256 hash of its content for integrity verification.
- Checkpoint storage location and hash MUST be recorded in the training job provenance record.

### 4.3 Fault Tolerance

- Ray Train MUST be configured to automatically recover failed workers and resume from the last
  valid checkpoint.
- Worker failure and recovery events MUST be logged as audit events.

### 4.4 Training Event Audit Logging

- Start, epoch completion, checkpoint, and end events MUST each generate an audit log entry with
  job ID, epoch number (where applicable), timestamp, and metrics snapshot.

---

## 5. Ray Data Pipeline

### 5.1 Data Transformation Logging

- Every transformation stage (map, filter, groupby, join) MUST log the stage name, input record
  count, output record count, and operator identity.

### 5.2 Lineage Tracking

- Source dataset URIs and target output URIs MUST be linked in a lineage record stored in the
  CK backend.
- The lineage record MUST be queryable to answer "which datasets were used to produce this
  output?"

### 5.3 Partitioning Strategy Documentation

- The partitioning strategy (random, stratified, sorted) MUST be documented and stored in the
  pipeline configuration.
- Changes to the partitioning strategy MUST generate an audit event.

### 5.4 Performance Metrics

- Data pipeline throughput (records/second) and end-to-end latency MUST be measured and
  exported to the monitoring system.

### 5.5 Audit Trail of Data Operations

- All read, write, transform, and delete operations on Ray Data datasets MUST be logged as
  audit events.

---

## 6. Ray Workflows

### 6.1 Explicit Step Dependencies

- Workflow DAGs MUST explicitly declare all step dependencies.
- Implicit ordering via shared side-effects is PROHIBITED.

### 6.2 Output Immutability

- Step outputs MUST be written to content-addressable, immutable storage.
- A step MUST NOT overwrite the output of another step.

### 6.3 Audit Logging of Workflow Execution

- Workflow creation, step start, step completion, step failure, and workflow completion events
  MUST all generate audit log entries.

### 6.4 Retry Policies

- Retry policies (maximum retries, backoff strategy) MUST be declared explicitly for each step.
- Each retry attempt MUST be logged as a distinct audit event with the failure reason.

---

## References

- Ray documentation: https://docs.ray.io/en/latest/
- Ray security guide: https://docs.ray.io/en/latest/ray-security/
- NIST SP 800-53 Rev. 5 AU-2, AU-12 (Audit)
- NIST SP 800-53 Rev. 5 SC-8 (Transmission Confidentiality)
- NIST SP 800-53 Rev. 5 SI-7 (Software Integrity)
