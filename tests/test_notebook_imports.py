"""Verify that every notebook is valid JSON and its imports are resolvable."""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

import pytest

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"

EXPECTED_NOTEBOOKS = [
    "01-warehouse.ipynb",
    "02-data-lake.ipynb",
    "03-lakehouse.ipynb",
    "04-virtualization.ipynb",
    "05-data-mesh.ipynb",
    "06-rag-mdm.ipynb",
]

# Heavy ML/AI libraries — just check they are installed, don't fully import
SKIP_FULL_IMPORT = {
    "torch",
    "sentence_transformers",
    "docling",
    "transformers",
    "tensorflow",
}

_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+([\w\.]+)", re.MULTILINE
)


def _extract_top_level_modules(notebook_path: Path) -> set[str]:
    """Extract top-level module names from import statements in code cells."""
    with open(notebook_path) as fh:
        nb = json.load(fh)
    modules: set[str] = set()
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        for match in _IMPORT_RE.finditer(source):
            top = match.group(1).split(".")[0]
            modules.add(top)
    return modules


@pytest.mark.parametrize("notebook_name", EXPECTED_NOTEBOOKS)
def test_notebook_is_valid_json(notebook_name: str) -> None:
    """Each notebook must be a well-formed .ipynb (JSON) file."""
    path = NOTEBOOKS_DIR / notebook_name
    assert path.exists(), f"Notebook not found: {path}"
    with open(path) as fh:
        data = json.load(fh)
    assert "cells" in data, "Missing 'cells' key — not a valid notebook"
    assert "metadata" in data, "Missing 'metadata' key — not a valid notebook"


@pytest.mark.parametrize("notebook_name", EXPECTED_NOTEBOOKS)
def test_imports_are_resolvable(notebook_name: str) -> None:
    """Every imported module should be findable (installed)."""
    path = NOTEBOOKS_DIR / notebook_name
    if not path.exists():
        pytest.skip(f"Notebook {notebook_name} not found")

    modules = _extract_top_level_modules(path)
    # Filter out standard-library modules that importlib always finds
    failures: list[str] = []
    for mod in sorted(modules):
        if mod.startswith("_"):
            continue
        if mod in SKIP_FULL_IMPORT:
            # Just verify the package metadata is findable
            spec = importlib.util.find_spec(mod)
            if spec is None:
                failures.append(mod)
            continue
        try:
            importlib.import_module(mod)
        except ImportError:
            failures.append(mod)

    assert not failures, (
        f"Notebook {notebook_name} imports modules that are not installed: "
        + ", ".join(failures)
    )
