.PHONY: init doctor status ready validate release buzz-dry-run

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
