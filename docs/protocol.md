# Research protocol: selected public *E. coli* genomes

## 0. Design before analysis

Select 5–20 genuine public *E. coli* assemblies from NCBI Datasets. This is a **methods portfolio**, not a representative surveillance sample. Define the sampling frame, inclusion/exclusion criteria, accession version, BioProject and citation for every assembly. Avoid duplicate GCA/GCF references for the same isolate unless explicitly justified.

Retain retrieval timestamps and software/database versions. Never invent accessions or phenotype metadata.

## 1. Dependencies

- Python 3.10+ (core Python scripts use only the standard library).
- NCBI Datasets CLI v2 (`datasets`), Bash and `unzip` on Linux/WSL2.
- NCBI AMRFinderPlus and its reference database, installed and updated as described at [NCBI AMRFinderPlus](https://github.com/ncbi/amr/wiki/Installing-AMRFinder).

Start with `environment.yml` (not a version-locked specification):

```bash
conda env create -f environment.yml
conda activate ecoli-amr-portfolio
amrfinder --update
```

Verify installed commands and capture `datasets --version`, `amrfinder --version` and database version. Resolve any CLI/version changes against NCBI documentation before running.

Windows users: execute local Python tests in PowerShell with `py -3`. Run shell scripts and AMRFinderPlus in WSL2/Ubuntu.

## 2. Verify and validate a local manifest

```powershell
Copy-Item data/manifest_template.csv data/manifest.csv
# Add public, verified GCA_ or GCF_ assembly accessions and BioProject metadata.
py -3 scripts/validate_manifest.py --manifest data/manifest.csv
```

The file schema is `sample_id,assembly_accession,bioproject,source_note`. Use unique, safe `sample_id` strings without spaces. The validator is **designed to fail** on the header-only template.

## 3. Retrieve and stage assemblies

From the repository root in a configured Linux/WSL2 environment:

```bash
bash scripts/download_assemblies.sh
```

This uses `datasets download genome accession` with a previously validated accession list, unpacks NCBI FASTA files, and copies them into `data/assemblies/{sample_id}.fna`. The script reports missing assemblies instead of silently dropping them.

## 4. Descriptive assembly QC

```bash
python3 scripts/assembly_qc.py
```

Produces `results/assembly_qc.csv` containing total bases, number of contigs, N50, GC%, and N%. These are descriptive metrics rather than automatic biological QC pass/fail calls. Investigate apparent outliers, species assignment, assembly completeness and contamination using an appropriate validated tool if needed.

## 5. AMRFinderPlus screening

With AMRFinderPlus and database installed:

```bash
bash scripts/run_amrfinder.sh
```

Underlying command per assembly:

```bash
amrfinder --nucleotide data/assemblies/your_sample.fna --organism Escherichia --threads 2 --output results/amrfinder/your_sample.tsv
```

Use organism-specific options only on verified *E. coli* genomes. This method may report organism-specific mutations depending on input and database; absence of a mutation call is not proof of absence of phenotypic resistance.

## 6. Summaries and separated mutation evidence

```bash
python3 scripts/summarize_amrfinder.py
```

Parser selects `Element type = AMR`. AMR `Element subtype` starting with `POINT` is summarized separately from all other AMR gene-symbol detections. The output includes:
- `sample_amr_summary.csv`: hit counts and numbers of unique symbols for each sample.
- `gene_presence_matrix.csv`: descriptive sample-by-gene binary matrix.
- `gene_prevalence.csv`: fraction with a gene within **this selected collection**, never epidemiological population prevalence.
- `point_mutation_presence_matrix.csv`: mutation calls in a separate matrix.

Neither gene detection nor reported substitutions are equivalent to an AST result.

## 7. Optional publication-quality graphics

```bash
python3 -m pip install -r requirements-figures.txt
python3 scripts/plot_gene_prevalence.py
```

The figure is withheld until real, audited input exists. Its label explicitly reports within-sample-set detection.

## 8. Reproducibility and release audit

- [ ] Accession, assembly version, source paper/BioProject and metadata independently checked.
- [ ] Study selection criteria and all exclusions documented.
- [ ] Software, database release and exact command parameters recorded.
- [ ] Assembly QC evaluated with biologically justified checks.
- [ ] AMRFinderPlus input/output tables and parsing audited.
- [ ] Clonal duplication and sampling differences considered.
- [ ] References, figure scripts, and results aligned.
- [ ] No private or unpublished datasets committed.

## Official sources

- NCBI Datasets CLI: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/command-line/datasets/download/genome/datasets_download_genome_accession/
- NCBI AMRFinderPlus: https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/
- Result interpretation: https://github.com/ncbi/amr/wiki/Interpreting-results
