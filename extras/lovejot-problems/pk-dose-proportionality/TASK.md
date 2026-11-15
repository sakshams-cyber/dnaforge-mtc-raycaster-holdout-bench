# HoldoutBench — Task 2: Reconstruct Dog Plasma Exposure

You are reviewing source data for investigational siRNA 2439-exNA. You may access the authorized local file `BioA_dog_plasma.tsv` and the sponsor's pharmacokinetics written summary PDF if staged in your environment. You must compute from the TSV, not copy an exposure table from the PDF.

1. For male and female dogs separately, for doses 20, 60, and 200 mg, reconstruct **observed Cmax per animal** and **AUC0–24 by linear trapezoids per animal**, then report the arithmetic group means (n=6 per sex/dose). Restrict this part to nominal times 0, 0.5, 4, 8, 12, and 24 hours. At each time use zero if concentration < the corresponding LLOQ; do not combine different animals into a composite profile. Provide two actual source animal IDs for each sex/dose group.
2. Calculate the ratio of group-mean Cmax and AUC0–24 for 20→60, 60→200, and 20→200 mg, separately by sex. Distinguish administered-dose ratios from measured-exposure ratios.
3. Classify dose proportionality overall (20 to 200 mg). Compare your conclusion to the regulatory PK written summary, **without alleging a discrepancy merely because AUC0–24 and AUClast/AUC∞ are different parameters**.
4. Identify limitations: BLQ substitution, uneven 24-vs-72-hour observation periods, nonidentity of AUC0–24 and reported AUClast, inability to infer a validated AUC∞ using this task's calculations, and between-animal variability.

Output only JSON with `source_file`, `analysis_window_hours`, `cmax_units`, `auc_units`, `results`, `conclusion`, `report_comparison` and `limitations`. Nest `groups` and `ratios` under each sex. Use `n`, `cmax_mean_ng_ml`, `auc0_24_mean_ng_h_ml` and `evidence_animal_ids` for a dose group. Use `cmax_ratio` and `auc0_24_ratio` for each dose pair. The local reference must supply the accepted conclusion, report comparison and limitation codes to the grader.

This is a *0–24-hour partial reconstruction*, not a claim to reproduce the sponsor's complete noncompartmental analysis. Scientific conclusions must not be extrapolated into human clinical safety recommendations.
