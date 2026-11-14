# Team-matching post

**Raycaster track: building "Holdout," an AI reviewer that finds clinical-hold problems in IND filings before submission.**

It reads a real IND, pulls every NOAEL, starting dose and study with its page, then checks it against FDA and ICH guidance (starting-dose math, study durations vs. trial length, genotox and safety pharmacology, numbers that disagree between the tox tables, the IB and the protocol). We're also building a benchmark of planted errors so we can show it beats a frontier model reading the filing alone.

The scaffold, rule engine and benchmark harness are ready; Saturday is about the real filings and results.

Looking for:
- **Toxicology / pharmacology / regulatory / clinical** person (most wanted): you'll own ground truth and answer the judges' science questions. No coding needed.
- **ML or backend engineer**: benchmark runs on Modal, results.
- **Designer or front-end engineer**: UI polish and the demo.

DM me — Saksham.
