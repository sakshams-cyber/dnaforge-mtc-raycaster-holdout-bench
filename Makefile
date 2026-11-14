PY ?= python3
BASES ?= fixtures/synthetic_ind_clean.md

.PHONY: help install test fixtures pdf demo analyze-pdf serve bench bench-baseline modal-serve modal-deploy modal-bench clean

help:
	@echo "make install         install Python deps"
	@echo "make test            run the test suite (offline)"
	@echo "make fixtures        regenerate the synthetic filings (.md + .pdf)"
	@echo "make demo            analyze the demo filing, print the memo"
	@echo "make analyze-pdf     same, through the PDF path"
	@echo "make serve           UI on http://127.0.0.1:8000"
	@echo "make bench           HoldoutBench on BASES with the holdout + null agents"
	@echo "make bench-baseline  add the model-alone baseline (needs ANTHROPIC_API_KEY)"
	@echo "make modal-serve     UI on a public Modal URL"
	@echo "BASES='real1.pdf real2.pdf' make bench   to benchmark on real filings"

install:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest -q

fixtures pdf:
	$(PY) fixtures/make_fixtures.py

demo:
	$(PY) -m holdout analyze fixtures/synthetic_ind_demo.md

analyze-pdf:
	$(PY) -m holdout analyze fixtures/synthetic_ind_demo.pdf --memo demo_memo.md --json demo_report.json

serve:
	$(PY) -m holdout serve --port 8000

bench:
	$(PY) -m holdout bench make $(foreach b,$(BASES),--base $(b)) --per-op 3
	$(PY) -m holdout bench run --agent holdout
	$(PY) -m holdout bench run --agent null
	$(PY) -m holdout bench score

bench-baseline:
	$(PY) -m holdout bench run --agent baseline --workers 4
	$(PY) -m holdout bench score

modal-serve:
	modal serve modal_app.py

modal-deploy:
	modal deploy modal_app.py

modal-bench:
	modal run modal_app.py::bench --agent holdout
	modal run modal_app.py::bench --agent baseline
	$(PY) -m holdout bench score

clean:
	rm -rf bench_out .cache demo_memo.md demo_report.json .pytest_cache

# Raycaster evaluation environment targets (new primary workflow)
.PHONY: eval-test eval-smoke eval-sync

eval-test:
	$(PY) -m pytest -q tests graders

eval-smoke:
	$(PY) scripts/stage.py --pack-root fixtures/eval_smoke --task examples/plumbing-smoke
	cp fixtures/eval_smoke/oracle.json examples/plumbing-smoke/solution/answer.json
	$(PY) scripts/sync_gradelib.py examples/plumbing-smoke
	$(PY) scripts/sanity.py examples/plumbing-smoke

eval-sync:
	$(PY) scripts/sync_gradelib.py

.PHONY: eval-preflight eval-numeric-smoke

eval-preflight:
	$(PY) scripts/preflight_eval.py

eval-numeric-smoke:
	$(PY) scripts/stage.py --pack-root fixtures/eval_numeric_smoke --task examples/numeric-smoke
	cp fixtures/eval_numeric_smoke/oracle.json examples/numeric-smoke/solution/answer.json
	$(PY) scripts/sync_gradelib.py examples/numeric-smoke
	$(PY) scripts/sanity.py examples/numeric-smoke --output out/numeric-sanity.json
