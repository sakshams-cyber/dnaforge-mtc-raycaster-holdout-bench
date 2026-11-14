> Superseded on Nov 14 by the eval-environment pivot. Use root README.md and AGENTS.md. Retained as setup history.

# Start Saturday, November 14, 2026 (Pacific)

Preparation only was authorized on Nov 13. AGENTS.md is the main build brief;
its instructions to implement M1 onward apply on event day, not during setup.
Application code, rules, UI and tests have been left as supplied.

## Open the environment

```bash
cd /Users/saksham/Documents/holdout
source .venv/bin/activate
python --version
make test
make demo
make serve
```

Open http://127.0.0.1:8000 and choose Load demo filing. Stop the server with Ctrl-C.
No frontend install or build is required. If not activating the environment,
use `make PY=.venv/bin/python test` (and similarly for demo/serve).

## At check-in / 9 AM

- Confirm whether the disclosed starter is allowed and whether filing pages may
  be sent to Anthropic. Keep real filings local until the data terms are clear.
- Before event implementation, create the baseline exactly once:

```bash
git init
git add -A
git status --short
# Check .env, .venv, data, reports, out and bench_out are absent from staging.
git commit -m "Pre-event scaffold (prepared Nov 11; see DISCLOSURE.md)"
git tag pre-event
```

The tag is intentionally not created during Nov 13 setup. DISCLOSURE.md also
records the Nov 13 environment preparation. Never backdate commits.

- Edit the local, ignored `.env` to add ANTHROPIC_API_KEY. Do not paste it into chat.
  Keep HOLDOUT_LLM=heuristic until the live API smoke test in AGENTS.md §6.2.
  The supplied model name is unverified; if rejected, confirm an available model
  with the team rather than guessing. No live API calls were needed for setup.
- Modal authentication and secrets are optional and remain event-day work.
- Poppler (`pdftoppm`, `pdftotext`) and Tesseract were absent at setup. Only install
  system packages if scanned filings require OCR and the owner approves.
- Put filings under data/raycaster/; hand keys under data/keys/.
- Read AGENTS.md §6–8. M0 still requires the API smoke test and pre-event tag;
  environment preparation alone does not satisfy the full gate.

## Gates

9:30 setup · 10:30 inventory + hand key · 12:30 extraction · 13:30 dose chain ·
15:00 initial baseline comparison · 16:30 cached demo · 16:45 final reports + review ·
17:15 feature freeze · 18:10 rehearsed demo kit · 18:15–19:15 table judging.

AGENTS.md supersedes the starter's older DAY_PLAN and PITCH schedule.
Do not treat synthetic validation as measured performance on real filings.
