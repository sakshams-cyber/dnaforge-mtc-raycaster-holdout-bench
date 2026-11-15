# Reconstruct dog plasma exposure from the raw bioanalytical data

You are reviewing source data for the investigational siRNA 2439-exNA. The workspace holds
one file, `/app/workspace/BioA_dog_plasma.tsv`: individual plasma concentrations from the
dog toxicology study, one row per animal and time point. Compute from that file.

1. For male and female dogs separately, at 20, 60 and 200 mg, compute **observed Cmax per
   animal** and **AUC0-24 per animal by linear trapezoids**, then report the arithmetic
   group means (n = 6 per sex and dose). Use only nominal times 0, 0.5, 4, 8, 12 and 24
   hours. Where a concentration is below that row's LLOQ, use zero. Do not pool animals
   into a composite profile.
2. For each sex, give the ratio of group-mean Cmax and of group-mean AUC0-24 for
   20 to 60 mg, 60 to 200 mg, and 20 to 200 mg (higher dose over lower dose).
3. State whether exposure is dose-proportional over 20 to 200 mg. Divide each sex's
   20-to-200 AUC0-24 ratio by the 10-fold dose ratio and apply the conventional
   0.80 to 1.25 band: above 1.25 is greater than proportional, below 0.80 is less.
   If the two sexes fall in different categories, answer `mixed_by_sex`.
4. For each sex and dose, name two animal IDs from that group as evidence.

This is a 0 to 24 hour partial reconstruction, not the sponsor's full noncompartmental
analysis. Do not report AUClast or AUC to infinity.

## Output

Give the source file, analysis window and units. For each sex, list the
group size, mean Cmax, mean AUC0–24 and two animal IDs for each dose. Report
both ratios for each dose pair and give the overall conclusion. The means
must agree within 0.5% and the ratios within 1%.
