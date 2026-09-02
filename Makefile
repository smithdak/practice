.PHONY: init doctor status ready validate release buzz-dry-run \
	checks agents packets cadence metrics triage brief

init:
	./scripts/init.sh

doctor:
	./scripts/doctor.sh

status:
	python3 scripts/taskctl.py status

ready:
	python3 scripts/taskctl.py ready

validate:
	python3 scripts/validate.py

release:
	python3 scripts/validate.py --release

buzz-dry-run:
	python3 scripts/buzz_bootstrap.py --dry-run

# Every check CI runs, in the same order.
checks:
	python3 -m unittest discover -s tests
	python3 scripts/validate.py --release
	python3 scripts/validate_artifacts.py
	python3 skills/evals/validate.py --root .
	python3 scripts/validate_agents.py --root .
	python3 scripts/validate_agent_evals.py --root .
	python3 scripts/triage.py validate ops/triage --root .
	python3 scripts/check_links.py

agents:
	python3 scripts/validate_agents.py --root .
	python3 scripts/validate_agent_evals.py --root .

# Validate agent packets: make packets PACKETS="path/to/packet.md"
packets:
	python3 scripts/validate_packet.py $(PACKETS) --root .

# Reports, not gates. Neither one blocks a build.
cadence:
	python3 scripts/cadence.py --root .

metrics:
	python3 scripts/collect_metrics.py --root .

triage:
	python3 scripts/triage.py validate ops/triage --root .

# Draft a release brief for human approval: make brief SINCE=<rev> AS_OF=<date>
brief:
	python3 scripts/release_brief.py --since $(SINCE) --as-of $(AS_OF) --root .
