# Reproducible Genomic AMR Screening in Public *Escherichia coli* Assemblies

**Status: workflow scaffold v0.1. No real study results have been generated or independently validated.**

An independent, research-oriented portfolio demonstrating reproducible curation of **public** *E. coli* genome assemblies, descriptive assembly quality metrics, antimicrobial-resistance determinant screening with NCBI AMRFinderPlus, and transparent summaries. This is **not** a clinical diagnostic assay or an epidemiological prevalence study.

## Research objective

Which antimicrobial-resistance gene symbols and mutation determinants are detected in a small, explicitly curated sample of public *E. coli* assemblies?

The pilot will use 5–20 publicly available NCBI GCA_/GCF_ assemblies. **No accessions have yet been selected.**

## Workflow

1. Curate an accession manifest with verified BioProject/source information.
2. Download public assemblies using NCBI Datasets CLI and map each accession to a stable sample ID.
3. Calculate descriptive assembly metrics: contig count, total bases, N50, GC%, and N%.
4. Run AMRFinderPlus for *Escherichia* against each genome, with tool and database versions recorded.
5. Produce **separate** AMR gene and point-mutation presence summaries.
6. Report detection fractions **within the selected sample only**, with provenance, limitations, and reproducible plotting scripts.

## Reproducibility

Run tests (Windows, Python 3.10+):

```powershell
py -3 -m unittest discover -s tests -v
```

Create a local manifest:

```powershell
Copy-Item data/manifest_template.csv data/manifest.csv
py -3 scripts/validate_manifest.py --manifest data/manifest.csv
```

The manifest validator **must fail** until verified public assembly accessions are provided.

Linux/WSL2 pipeline (external `datasets` and `amrfinder` installation required):

```bash
bash scripts/download_assemblies.sh
python3 scripts/assembly_qc.py
bash scripts/run_amrfinder.sh
python3 scripts/summarize_amrfinder.py
```

See [the protocol](docs/protocol.md) and [maintenance guidance](PUBLISHING.md). GitHub Actions runs synthetic-data unit tests only, not sequencing analysis.

## Scientific boundaries

- Gene presence does **not** demonstrate phenotypic antibiotic resistance or MIC.
- Assembly quality and method/database versions affect detectability.
- Screening fractions in a convenience sample are **not** population prevalence.
- Cross-BioProject comparisons require careful consideration of source/study confounding.
- Do not commit confidential clinical material or unpublished thesis data.

## Project independence

This independent starter is distinct from the author's thesis WGS project involving 189 *E. coli* isolates. No thesis-specific results, patient data, or unpublished datasets are included here. Future code, datasets, figures, and conclusions will be committed only after they are verified.

## Primary resources

- [NCBI Datasets](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/command-line/datasets/download/genome/datasets_download_genome_accession/)
- [NCBI AMRFinderPlus](https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/)
- [Interpretation of AMRFinderPlus results](https://github.com/ncbi/amr/wiki/Interpreting-results)

## License

Source code and project text released under the MIT License. Original sequence authors and sources retain their data rights and must be cited.
