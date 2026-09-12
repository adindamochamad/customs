.PHONY: install dev demo test lint clean verify-clone audit-secrets prep-video submission-check init-repo print-submission

install:
	python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

dev:
	.venv/bin/uvicorn customs.main:app --reload --port 8787

demo:
	.venv/bin/python -m demo.scenario

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check customs demo tests scripts

clean:
	rm -rf .venv .pytest_cache **/__pycache__ customs.db

verify-clone:
	bash scripts/verify_clean_clone.sh

audit-secrets:
	bash scripts/audit_git_secrets.sh

prep-video:
	bash scripts/prep_video.sh

submission-check:
	bash scripts/submission_readiness.sh

init-repo:
	bash scripts/init_public_repo.sh

print-submission:
	bash scripts/print_submission_fields.sh

export-slides:
	bash scripts/export_slides_pdf.sh
