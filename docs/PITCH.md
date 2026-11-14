# Pitch: 3 minutes, then questions

Fill the [brackets] at 5:30 PM from `bench_out/results.md` and the domain lead's flag review.

## Script

**Hook (20 s).** "About one in eleven first INDs goes on clinical hold within 30 days. One of the legal grounds is an investigator brochure that is erroneous or incomplete. We built the reviewer that catches that before you file. It's called Holdout."

**Live demo (90 s).**
1. Drop a Raycaster filing on the page. "It maps the filing — overview, tox tables, IB, protocol — and pulls every NOAEL, starting dose and study with its page."
2. Starting-dose panel: "Dog NOAEL on page [7], divide by 1.8, times 60 kilos, divide by 10: [33] milligrams. The protocol proposes [50]." Click the chip; the page opens with the number highlighted.
3. Click the top red flag. "Why? The overview, the IB and the protocol say [30]; the tox table says [10]. The rationale used the stale number." Both pages side by side.
4. "Every flag is a deterministic rule with its guidance citation. The model only reads; Python decides. And before anything is reported, we re-read the cited page — if the quote isn't there, it's not a finding."

**Proof (40 s).** Switch to the Benchmark tab. "We built HoldoutBench: [N] planted errors across [M] real filings, eight error types, with clean copies to catch false alarms. [Model] alone caught [X]%. Holdout caught [Y]%, every one with a page. On the unmodified filings, Holdout raised [K] issues; our [toxicologist/clinician] confirmed [J]."

**Close (30 s).** "This is the check Raycaster's users want before they file, and HoldoutBench is a yardstick any regulatory AI can be scored on — it runs on BenchFlow and Modal today. Next: CMC checks, the most common hold reason."

## Slide outline (5 slides max; the demo carries it)

1. Title: Holdout — find the clinical hold before the FDA does. One line: who we are.
2. Problem: 125 of 1,410 first INDs on hold in 30 days (FDA FY2013); 21 CFR 312.42(b)(1)(iii). One sentence.
3. How it works: the architecture picture (ingest → extract → rules → verify → report; HoldoutBench underneath).
4. Results: the chart + one sentence. Real findings on unmodified filings, if any.
5. What's next + ask: CMC rules, exposure margins, Raycaster integration; "we'd love to keep building this."

## Questions to prepare for

| Question | Answer |
| --- | --- |
| Isn't this just an LLM reading a PDF? | The model only extracts facts with page quotes. Flags come from deterministic rules; a verification pass checks every quote is on its page. |
| How do you know it's right? | HoldoutBench: planted errors with an answer key, clean copies for false alarms, differential scoring. Show the table. |
| Planted errors aren't real errors. | Agreed — so we also report what it found on the unmodified filings, reviewed by [domain lead]. |
| Biologics? Oncology? | Rules branch: ICH S9 for oncology patients; mg/kg scaling and one-species warnings for biologics; MABEL flagged as out of scope. |
| Would FDA accept this? | It's a pre-submission screen, like a linter. The sponsor stays accountable. |
| What did you build today? | `DISCLOSURE.md`: scaffold before; real-filing extraction, benchmark results, tuning and UI today. |
| Why not just use Raycaster? | We'd be its check layer, and HoldoutBench can score their agent too. |
| What happens with redactions? | Redacted values are never guessed; the rule reports "cannot verify". |

## Demo hygiene

- Pre-load the best filing in a second tab; keep the backup video open in a third.
- Zoom the browser to 125% for the room. Close Slack and notifications.
- If Wi-Fi dies: `make serve` on localhost with the heuristic extractor still works (cached Claude results also replay from `.cache/llm`).
