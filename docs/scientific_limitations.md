# Interpretation boundaries

This project is a training and reproducibility workflow. Biological interpretation must be based on outputs from a genuinely curated public cohort.

1. **Genotypes are not phenotypes.** Reported resistance-associated determinants alone do not establish clinical susceptibility, MICs, or treatment recommendations; laboratory AST would be required.
2. **Assembly limitations.** Fragmentation, incomplete assemblies, contamination, missing plasmids, repeats and annotation differences may change determinant detection.
3. **AMRFinderPlus terminology.** Non-POINT AMR hits are reported as gene-symbol detections and POINT* subtypes are counted separately. Do not assume that distinct rows correspond to biologically independent mechanisms.
4. **Sampling and confounding.** A small purposive set of 5–20 genomes cannot estimate population AMR prevalence. Cross-BioProject comparisons may be confounded by source, time, site and sequencing methodology.
5. **Biofilm claims.** This pipeline does not measure biofilm phenotypes. It is an AMR genomic screening workflow, not an assay of biofilm formation.
6. **Genomic context.** These scripts do not establish plasmid or chromosome localization of determinants.
7. **Reproducibility.** Results can vary by assembly version and software/database release; version-locking and provenance are essential.
