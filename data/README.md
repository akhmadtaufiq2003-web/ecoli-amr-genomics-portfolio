# Data directory

`manifest_template.csv` contains **only a header**, intentionally. No sample is assumed to be part of this demonstration.

Copy the file to `manifest.csv` and add documented public NCBI assemblies. See `docs/protocol.md`.

- `sample_id`: stable label, letters/digits/underscores/hyphens, unique per row.
- `assembly_accession`: NCBI GCA_ or GCF_ accession; use the version suffix when available.
- `bioproject`: verified NCBI BioProject (do not guess it from the accession).
- `source_note`: provenance or original paper citation (do not infer phenotype).

The local manifest, downloaded FASTA, and NCBI metadata are ignored by Git for safety. A public manifest can be committed separately only after provenance and data-sharing review.
