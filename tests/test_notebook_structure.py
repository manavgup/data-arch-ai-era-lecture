"""Validate that every notebook follows the 7-section template from SPEC.md section 2.

Required sections (in order):
  1. The pattern in one paragraph
  2. When you'd use it, when you wouldn't
  3. The setup
  4. Three canonical queries (with Q1, Q2, Q3 sub-headings)
  5. Where this pattern breaks
  6. The IBM stack mapping
  7. BFSI reality check

Additional checks:
  - No empty code cells
  - Notebook title cell exists (H1)
  - No corporate-speak phrases (SPEC.md §8 rule 9)
"""

from __future__ import annotations

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

# Section heading patterns — matched case-insensitively against markdown cells.
# Each pattern must appear in at least one markdown cell heading.
REQUIRED_SECTIONS = [
    (1, re.compile(r"section\s*1.*pattern.*paragraph", re.IGNORECASE)),
    (2, re.compile(r"section\s*2.*when.*you.*use", re.IGNORECASE)),
    (3, re.compile(r"section\s*3.*setup", re.IGNORECASE)),
    (4, re.compile(r"section\s*4.*canonical\s*quer", re.IGNORECASE)),
    (5, re.compile(r"section\s*5.*break", re.IGNORECASE)),
    (6, re.compile(r"section\s*6.*ibm.*stack", re.IGNORECASE)),
    (7, re.compile(r"section\s*7.*bfsi.*reality", re.IGNORECASE)),
]

# Canonical query labels (SPEC.md §2: Q1, Q2, Q3).
# May appear as markdown headings (### Q1:) or code cell comments (# ── Q1:).
QUERY_PATTERNS = [
    re.compile(r"Q1[:\s]", re.IGNORECASE),
    re.compile(r"Q2[:\s]", re.IGNORECASE),
    re.compile(r"Q3[:\s]", re.IGNORECASE),
]

# Corporate-speak phrases to reject (SPEC.md §8 rule 9)
CORPORATE_SPEAK = [
    "synergy",
    "leverage our",
    "move the needle",
    "circle back",
    "thought leader",
    "paradigm shift",
    "at the end of the day",
    "low-hanging fruit",
]

# ── Helpers ──────────────────────────────────────────────────────────────────


def _load_notebook(path: Path) -> dict:
    with open(path) as fh:
        return json.load(fh)


def _markdown_cells(nb: dict) -> list[str]:
    """Return the concatenated source of each markdown cell."""
    return ["".join(cell.get("source", [])) for cell in nb.get("cells", []) if cell.get("cell_type") == "markdown"]


def _code_cells(nb: dict) -> list[tuple[int, str]]:
    """Return (cell_index, source) for each code cell."""
    results = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            results.append((i, src))
    return results


def _all_markdown_text(nb: dict) -> str:
    return "\n".join(_markdown_cells(nb))


def _all_cell_text(nb: dict) -> str:
    """Return all text from both markdown and code cells."""
    parts = []
    for cell in nb.get("cells", []):
        parts.append("".join(cell.get("source", [])))
    return "\n".join(parts)


# ── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("notebook_name", EXPECTED_NOTEBOOKS)
class TestNotebookStructure:
    """Each notebook must follow the 7-section template."""

    def test_notebook_has_title(self, notebook_name: str) -> None:
        """First cell should be a markdown H1 title."""
        path = NOTEBOOKS_DIR / notebook_name
        if not path.exists():
            pytest.skip(f"Notebook not found: {path}")
        nb = _load_notebook(path)
        md_cells = _markdown_cells(nb)
        assert md_cells, f"{notebook_name}: no markdown cells found"
        first_md = md_cells[0].strip()
        assert first_md.startswith(
            "# "
        ), f"{notebook_name}: first markdown cell should be an H1 title, got: {first_md[:80]!r}"

    def test_all_seven_sections_present(self, notebook_name: str) -> None:
        """All 7 required sections must appear as markdown headings."""
        path = NOTEBOOKS_DIR / notebook_name
        if not path.exists():
            pytest.skip(f"Notebook not found: {path}")
        nb = _load_notebook(path)
        all_md = _all_markdown_text(nb)
        missing: list[int] = []
        for section_num, pattern in REQUIRED_SECTIONS:
            if not pattern.search(all_md):
                missing.append(section_num)
        assert not missing, (
            f"{notebook_name}: missing required sections: {missing}. "
            f"Expected headings matching the 7-section template from SPEC.md §2."
        )

    def test_sections_in_order(self, notebook_name: str) -> None:
        """Sections must appear in order (1 through 7)."""
        path = NOTEBOOKS_DIR / notebook_name
        if not path.exists():
            pytest.skip(f"Notebook not found: {path}")
        nb = _load_notebook(path)
        md_cells = _markdown_cells(nb)

        # Find first cell index where each section appears
        positions: dict[int, int] = {}
        for cell_idx, text in enumerate(md_cells):
            for section_num, pattern in REQUIRED_SECTIONS:
                if section_num not in positions and pattern.search(text):
                    positions[section_num] = cell_idx

        found = sorted(positions.keys())
        if len(found) < 2:
            pytest.skip(f"{notebook_name}: too few sections found to check order")

        for i in range(len(found) - 1):
            sec_a, sec_b = found[i], found[i + 1]
            assert positions[sec_a] < positions[sec_b], (
                f"{notebook_name}: Section {sec_a} (cell {positions[sec_a]}) "
                f"appears after Section {sec_b} (cell {positions[sec_b]})"
            )

    def test_three_canonical_queries(self, notebook_name: str) -> None:
        """Section 4 must contain Q1, Q2, Q3 labels (in markdown headings or code comments)."""
        path = NOTEBOOKS_DIR / notebook_name
        if not path.exists():
            pytest.skip(f"Notebook not found: {path}")
        nb = _load_notebook(path)
        all_text = _all_cell_text(nb)
        missing_qs: list[str] = []
        for i, qpat in enumerate(QUERY_PATTERNS, 1):
            if not qpat.search(all_text):
                missing_qs.append(f"Q{i}")
        assert not missing_qs, f"{notebook_name}: missing canonical query labels: {', '.join(missing_qs)}"

    def test_no_empty_code_cells(self, notebook_name: str) -> None:
        """Code cells should not be completely empty."""
        path = NOTEBOOKS_DIR / notebook_name
        if not path.exists():
            pytest.skip(f"Notebook not found: {path}")
        nb = _load_notebook(path)
        empty: list[int] = []
        for cell_idx, src in _code_cells(nb):
            if not src.strip():
                empty.append(cell_idx)
        assert not empty, f"{notebook_name}: empty code cells at indices: {empty}"

    def test_no_corporate_speak(self, notebook_name: str) -> None:
        """SPEC.md §8 rule 9: no corporate-speak in markdown content."""
        path = NOTEBOOKS_DIR / notebook_name
        if not path.exists():
            pytest.skip(f"Notebook not found: {path}")
        nb = _load_notebook(path)
        all_md = _all_markdown_text(nb).lower()
        found = [phrase for phrase in CORPORATE_SPEAK if phrase in all_md]
        assert not found, f"{notebook_name}: corporate-speak found: {found}"
