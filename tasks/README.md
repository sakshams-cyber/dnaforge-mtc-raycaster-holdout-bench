# Selected tasks

Final three tasks, subject to human-verified gold:

- hold-scope
- hold-objection-map
- recompute-reported-value

T1-B uses the partial hold letter for the requests and the filed IND for the
evidence. The folder did not contain a qualifying sponsor response. T3 and T4
are retired. The dataset-spec
workflow is paused beyond the local search and task setup requested here.
These scaffolds need human rules and verified gold before real runs.

Run local sanity for a prepared task with `python scripts/sanity.py tasks/<id>`.
`python scripts/sanity_fixtures.py` tests the same entrypoints with fictional inputs.

Search the extracted pack locally:

```bash
python scripts/extract_pdf_text.py
scripts/find.sh "clinical hold"
```

Run a prepared task's local container oracle with:

```bash
DOCKER_CONTEXT=colima-holdout .venv-harbor/bin/harbor run -p tasks/<id> -a oracle -o jobs/oracle
```

Put reviewer notes under ignored `data/gold_notes/`. For T1, include each
objection ID, category, status, and approved filed IND citation or an explicit
absence decision. For T5, include each activity ID and description, its status, and
decisive evidence. For T2, include the selected claim, units, method, tolerance,
and verified input coordinates. Include the verifier's name and what was checked.
`scripts/quote_ref.py` locates evidence offsets in the grader's normalized page
text. The PDF search helper uses a different extraction layout, so its character
positions are not suitable for quote references.

The T1-B blanket probe keeps the correct categories and changes every status
to `absent`. Because an absent item earns both status and null-citation credit,
the score stays below 0.4 only when fewer than 10% of the verified items are
absent. Report a failing probe without changing any reviewer label.
