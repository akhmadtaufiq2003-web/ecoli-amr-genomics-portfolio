"""Deterministic unit tests based solely on artificial data, not experimental results."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_manifest import validate_manifest
from assembly_qc import metrics
from summarize_amrfinder import parse_report, aggregate, write_reports
from stage_assemblies import stage


class TestStarter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, rows):
        p = self.root / "manifest.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["sample_id", "assembly_accession", "bioproject", "source_note"])
            w.writerows(rows)
        return p

    def test_manifest_valid_and_duplicate_rejected(self):
        p = self.manifest([["ecoli_01", "GCF_000005845.2", "PRJNA000000", "public test"]])
        self.assertEqual(len(validate_manifest(p)), 1)
        p = self.manifest([["ecoli_01", "GCF_000005845.2", "", ""], ["ecoli_01", "GCF_000005846.1", "", ""]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_manifest(p)

    def test_empty_manifest_rejected(self):
        p = self.manifest([])
        with self.assertRaisesRegex(ValueError, "No assemblies selected"):
            validate_manifest(p)

    def test_fasta_metrics(self):
        fasta = self.root / "s01.fna"
        fasta.write_text(">ctg1\nACGTNN\n>ctg2\nGGAA\n", encoding="ascii")
        out = metrics(fasta)
        self.assertEqual(out["contig_count"], 2)
        self.assertEqual(out["total_bases"], 10)
        self.assertEqual(out["n50_bases"], 6)
        self.assertEqual(out["n_percent_total"], 20.0)
        self.assertEqual(out["gc_percent_total"], 40.0)

    def test_amr_gene_mutation_split_and_presence(self):
        folder = self.root / "amr"
        folder.mkdir()
        first = folder / "s01.tsv"
        first.write_text("Element symbol\tElement type\tElement subtype\n"
                         "blaTEM-1\tAMR\tAMR\n"
                         "blaTEM-1\tAMR\tAMR\n"
                         "gyrA_S83L\tAMR\tPOINT\n"
                         "qacEdelta1\tSTRESS\tSTRESS\n", encoding="utf-8")
        second = folder / "s02.tsv"
        second.write_text("Gene symbol\tElement type\tElement subtype\n"
                          "tet(A)\tAMR\tAMR\n"
                          "gyrA_D87N\tAMR\tPOINT_DISRUPT\n", encoding="utf-8")
        parsed = parse_report(first)
        self.assertEqual(parsed["gene_hits"], 2)
        self.assertEqual(len(parsed["genes"]), 1)
        self.assertEqual(parsed["mutation_hits"], 1)
        data = aggregate([first, second])
        output = self.root / "summary"
        write_reports(data, output)
        with (output / "gene_presence_matrix.csv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["blaTEM-1"], "1")
        self.assertEqual(rows[1]["blaTEM-1"], "0")
        self.assertEqual(rows[1]["tet(A)"], "1")

    def test_stage_keeps_sample_mapping(self):
        p = self.manifest([["my_ecoli", "GCF_000005845.2", "", ""]])
        genome = self.root / "package" / "ncbi_dataset" / "data" / "GCF_000005845.2"
        genome.mkdir(parents=True)
        (genome / "test_genomic.fna").write_text(">c1\nATGC\n")
        files = stage(p, self.root / "package", self.root / "assemblies")
        self.assertEqual(files[0].name, "my_ecoli.fna")
        self.assertEqual(files[0].read_text(), ">c1\nATGC\n")


if __name__ == "__main__":
    unittest.main()
