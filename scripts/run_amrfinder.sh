#!/usr/bin/env bash
# Run from the repository root in Linux/WSL with AMRFinderPlus installed.
set -euo pipefail
command -v amrfinder >/dev/null || { echo 'ERROR: amrfinder not installed; see docs/protocol.md' >&2; exit 2; }
mkdir -p results/amrfinder results/logs
printf 'AMRFinderPlus binary version:\n' > results/logs/tool_versions.txt
amrfinder --version >> results/logs/tool_versions.txt 2>&1 || true
printf '\nDatabase version:\n' >> results/logs/tool_versions.txt
amrfinder --database_version >> results/logs/tool_versions.txt 2>&1 || true
shopt -s nullglob
assemblies=(data/assemblies/*.fna data/assemblies/*.fa data/assemblies/*.fasta)
if (( ${#assemblies[@]} == 0 )); then
  echo 'ERROR: no .fna/.fa/.fasta assemblies found in data/assemblies/' >&2
  exit 2
fi
for assembly in "${assemblies[@]}"; do
  sample=$(basename "$assembly")
  sample=${sample%.*}
  echo "Running AMRFinderPlus on $sample"
  # Escherichia selection is appropriate ONLY for E. coli assemblies.
  amrfinder --nucleotide "$assembly" --organism Escherichia --threads 2 --output "results/amrfinder/${sample}.tsv"
done
echo 'Done. Next: python3 scripts/summarize_amrfinder.py'
