# Check what the IND contained when filed

You are an FDA reviewer. For each numbered item listed below, use the partial
clinical hold letter to identify what FDA asked for, then check whether the
filed IND documents in `/app/workspace/` already contain it. Use only the
supplied files. Classify each item using these definitions:

- `hold_deficiency`: the letter states this as a reason for the hold or as
  something needed before the hold can be lifted.
- `non_hold_comment`: everything else the letter asks or advises.
- `present`: the filed IND contains what FDA asked for, in the form requested.
- `partially_present`: only part of it is present, or it is in a weaker form,
  such as a shorter study or a plan instead of completed data.
- `absent`: the filed IND documents do not contain the requested item.

Use the item IDs listed below. For presence and evidence, use the filed IND
under `ind/`. The other documents in the hold folder provide context. Cite a filed
IND page with a verbatim quote of at least 20 characters. The hold letter
defines the request and cannot serve as evidence that the IND contained it.
Set `cite` to `null` if and only if the item is `absent`. Cite workspace-relative
paths and 1-based physical pages. Write `/app/output/answer.json`.

Hold letter: `partial-clinical-hold/IND_167326_PartialClinicalHoldLetter.pdf`.

- `hold-1` — hold letter page 2.
- `hold-2` — hold letter page 2.
- `comment-1` — hold letter page 2.
- `comment-2` — hold letter page 4.
- `comment-3` — hold letter page 3.

```json
{"items":[{"id":"hold-1","category":"hold_deficiency","status":"partially_present","cite":{"path":"example.pdf","page":2,"quote":"Evidence from the fictional filed document."}}]}
```
