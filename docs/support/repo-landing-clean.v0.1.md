# Repo Landing Clean v0.1

This landing shape excludes vendored build dependencies and prefers shared-root JSON Schemas with thin wrappers.

## Rules
1. Do not commit `.codegen_vendor`.
2. Commit canonical YAML, clean generated schemas, fixtures, docs, proto, descriptor sets, and validation reports.
3. Regenerate in CI and fail on manifest drift.
