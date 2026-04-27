.PHONY: validate action-ontology-validate cso-governance-validate cso-governance-scaffold multidomain-geospatial-validate

validate:
	./.venv/bin/python tools/validate.py 2>/dev/null || python3 tools/validate.py
	bash tools/action_ontology_validate_all.sh

multidomain-geospatial-validate:
	./.venv/bin/python tools/validate_multidomain_geospatial.py 2>/dev/null || python3 tools/validate_multidomain_geospatial.py

action-ontology-validate:
	bash tools/action_ontology_validate_all.sh

CSO_GOVERNANCE_OUTPUT ?= build/cso-governance-pack
CSO_GOVERNANCE_NAME ?= Generated Governed CSO Pack

cso-governance-validate:
	./.venv/bin/python scripts/validate_cso_partnership_examples.py 2>/dev/null || python3 scripts/validate_cso_partnership_examples.py
	./.venv/bin/python scripts/validate_cso_partnership_negative_and_hygiene.py 2>/dev/null || python3 scripts/validate_cso_partnership_negative_and_hygiene.py

cso-governance-scaffold:
	./.venv/bin/python scripts/scaffold_cso_partnership_pack.py --output "$(CSO_GOVERNANCE_OUTPUT)" --name "$(CSO_GOVERNANCE_NAME)" 2>/dev/null || python3 scripts/scaffold_cso_partnership_pack.py --output "$(CSO_GOVERNANCE_OUTPUT)" --name "$(CSO_GOVERNANCE_NAME)"
