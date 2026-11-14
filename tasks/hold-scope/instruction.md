# Determine what the partial clinical hold permits

You are an FDA reviewer. For each activity listed below, decide whether the
sponsor may do it now, under the partial clinical hold, using only the hold
letter and 21 CFR 312.42 in `/app/workspace/`. Every listed activity is decided
by those documents.

- `permitted`: explicitly allowed, or part of a study the letter says may
  proceed and not otherwise restricted.
- `not_permitted`: forbidden, or it requires starting, enrolling or dosing in
  the held study before FDA notifies the sponsor that it may proceed.

In an ongoing study on hold, existing participants must come off the drug
unless FDA specifically allows continued treatment. Sending a response does
not lift the hold. Cite the deciding sentence with a workspace-relative path,
a 1-based physical page, and a verbatim quote of at least 20 characters. Cite
the plain-text regulation as page 1. Write `/app/output/answer.json`.

**Draft: insert the human-approved activity list here.**

```json
{"activities":[{"id":"act-1","status":"not_permitted","cite":{"path":"example.pdf","page":2,"quote":"Evidence from the fictional example decision."}}]}
```
