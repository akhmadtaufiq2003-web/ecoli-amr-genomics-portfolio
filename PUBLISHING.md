# Repository publishing and maintenance

This starter scaffold has been uploaded to the public repository `akhmadtaufiq2003-web/ecoli-amr-genomics-portfolio`.

## Verify the source locally

```powershell
py -3 -m unittest discover -s tests -v
```

After publishing, inspect the **Actions** tab. Both Python 3.11 and 3.13 should run synthetic-data tests. Passing tests do not constitute validation of empirical AMR results.

## Add public-data analysis later

1. Verify accession provenance and metadata from NCBI before populating the local manifest.
2. Use only appropriately licensed public datasets; respect source restrictions.
3. Run QC and AMRFinderPlus with documented commands and database versions.
4. Record tool versions and parameters, and retain reproducible figures and scripts.
5. Never publish confidential clinical material, unpublished thesis data, or unsupported claims of phenotypic resistance.

Do not include local FASTA datasets in Git unless provenance, consent, data-use terms, and file size have been checked.
