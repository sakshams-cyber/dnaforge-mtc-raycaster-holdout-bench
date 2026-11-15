# Problem 3 — Can CSF levels establish drug clearance from brain tissue?

You are evaluating the IND 167326 dog biodistribution results for 2439-exNA. Use **only the provided** `BioA_dog_CSF.tsv` and `BioA_dog_tissue.tsv` to independently investigate whether cerebrospinal fluid (CSF) levels reliably indicate brain-tissue persistence from Day 2 to Day 29.

For **20, 60, and 200 mg**, **males and females**, and **CSF plus all six brain regions**:

1. Report number of samples, number quantifiable, and arithmetic mean among quantifiable values for each day. Do not treat `BQL` as zero. Keep `ng/mL` (CSF) and `ng/g` (tissue) distinct.
2. Report **Day29 mean / Day2 mean** only when **all samples in both groups are quantifiable**; otherwise report `null`. These are cross-sectional group comparisons, not longitudinal within-animal declines.
3. Identify any animal whose tissue measurements have no corresponding CSF animal record.
4. Investigate the unusually large 60 mg female putamen fold change. Name the animal driving the mean and state whether this proves drug accumulation.
5. Conclude what CSF measurements do and do not establish about measurable drug in brain tissue. Name key uncertainties: cohort differences, Day 29 sample size, BQL handling, unit differences, biological variability, missing CSF records.

Return ONLY a JSON object with `groups`, `missing_csf_animal_ids`, `outlier`, `conclusion` and `limitations`. Include **every dose/sex/region** combination. Each group has `day2` and `day29` objects with `n`, `quantified` and `mean_quantified`, plus `ratio_day29_day2`. The outlier has `dose_mg`, `sex`, `region`, `day`, `animal_id` and `interpretation` fields. Group keys are `{dose}|{sex}|{region}`, e.g. `60|M|CSF`. Use exact region labels from the tissue file. The analysis must be calculated from the raw TSVs; do not copy a conclusion from the written summary.

The benchmark compares exact IDs, counts, coded scientific conclusions, and numerics within a relative tolerance. This is a numerical/evidence screening task, not a definitive claim of safety or biological clearance.
