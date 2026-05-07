"""Validate generated data files: existence, schema, and row counts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── Parquet files and their expected columns / row-count ranges ──────────

PARQUET_FILES = {
    "customers.parquet": {
        "columns": {"customer_id", "name", "dob", "kyc_status", "risk_score", "segment"},
        "min_rows": 50_000,
        "max_rows": 150_000,
    },
    "accounts.parquet": {
        "columns": {"account_id", "customer_id", "branch_id", "account_type", "balance"},
        "min_rows": 100_000,
        "max_rows": 300_000,
    },
    "transactions.parquet": {
        "columns": {"transaction_id", "account_id", "amount", "timestamp"},
        "min_rows": 500_000,
        "max_rows": 1_500_000,
    },
    "branches.parquet": {
        "columns": {"branch_id", "name", "region", "manager_id"},
        "min_rows": 10,
        "max_rows": 100,
    },
}

MDM_FILE = DATA_DIR / "mdm" / "entity_links.parquet"

POLICY_DIR = DATA_DIR / "policies"
EXPECTED_POLICIES = [f"MTB-POL-{i:03d}.pdf" for i in range(1, 11)]

EVAL_FILE = DATA_DIR / "eval" / "aml_qa_eval.jsonl"
LINEAGE_FILE = DATA_DIR / "lineage" / "lineage_graph.json"


# ── Tests ────────────────────────────────────────────────────────────────


class TestParquetFiles:
    """Core tabular data files."""

    @pytest.mark.parametrize("filename", list(PARQUET_FILES.keys()))
    def test_file_exists(self, filename: str) -> None:
        path = DATA_DIR / filename
        assert path.exists(), f"Missing data file: {path}"

    @pytest.mark.parametrize("filename", list(PARQUET_FILES.keys()))
    def test_row_count_in_range(self, filename: str) -> None:
        path = DATA_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not generated yet")
        df = pd.read_parquet(path)
        spec = PARQUET_FILES[filename]
        assert spec["min_rows"] <= len(df) <= spec["max_rows"], (
            f"{filename}: row count {len(df)} outside [{spec['min_rows']}, {spec['max_rows']}]"
        )

    @pytest.mark.parametrize("filename", list(PARQUET_FILES.keys()))
    def test_expected_columns(self, filename: str) -> None:
        path = DATA_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not generated yet")
        df = pd.read_parquet(path)
        spec = PARQUET_FILES[filename]
        missing = spec["columns"] - set(df.columns)
        assert not missing, f"{filename}: missing expected columns {missing}"


class TestMDMEntityLinks:
    """MDM entity-link file."""

    def test_entity_links_exists(self) -> None:
        assert MDM_FILE.exists(), f"Missing MDM file: {MDM_FILE}"

    def test_entity_links_not_empty(self) -> None:
        if not MDM_FILE.exists():
            pytest.skip("entity_links.parquet not generated yet")
        df = pd.read_parquet(MDM_FILE)
        assert len(df) > 0, "entity_links.parquet is empty"


class TestPolicyPDFs:
    """Policy PDF documents."""

    @pytest.mark.parametrize("pdf_name", EXPECTED_POLICIES)
    def test_policy_pdf_exists(self, pdf_name: str) -> None:
        path = POLICY_DIR / pdf_name
        assert path.exists(), f"Missing policy PDF: {path}"

    @pytest.mark.parametrize("pdf_name", EXPECTED_POLICIES)
    def test_policy_pdf_not_empty(self, pdf_name: str) -> None:
        path = POLICY_DIR / pdf_name
        if not path.exists():
            pytest.skip(f"{pdf_name} not generated yet")
        assert path.stat().st_size > 0, f"{pdf_name} is empty"


class TestEvalAndLineage:
    """Eval JSONL and lineage JSON."""

    def test_eval_jsonl_exists(self) -> None:
        assert EVAL_FILE.exists(), f"Missing eval file: {EVAL_FILE}"

    def test_eval_jsonl_not_empty(self) -> None:
        if not EVAL_FILE.exists():
            pytest.skip("aml_qa_eval.jsonl not generated yet")
        lines = EVAL_FILE.read_text().strip().splitlines()
        assert len(lines) > 0, "aml_qa_eval.jsonl has no entries"

    def test_lineage_graph_exists(self) -> None:
        assert LINEAGE_FILE.exists(), f"Missing lineage file: {LINEAGE_FILE}"

    def test_lineage_graph_valid_json(self) -> None:
        if not LINEAGE_FILE.exists():
            pytest.skip("lineage_graph.json not generated yet")
        import json

        data = json.loads(LINEAGE_FILE.read_text())
        assert isinstance(data, dict), "lineage_graph.json root should be a dict"
