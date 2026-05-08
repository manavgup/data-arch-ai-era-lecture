#!/usr/bin/env python3
"""Generate 10 SVG architecture diagrams and convert them to PNG for PPTX embedding.

Produces:
  1. refarch-full.png       — Full IBM Software Hub reference architecture
  2. refarch-block1.png     — Storage + Access highlighted
  3. refarch-block2.png     — AI/ingestion highlighted, Docling + Context Forge gap callouts
  4. refarch-block3.png     — Governance + Security + Deploy highlighted
  5. pattern-lake.png       — Data Lake architecture
  6. pattern-lakehouse.png  — Lakehouse architecture
  7. pattern-mesh.png       — Data Mesh architecture
  8. pattern-fabric.png     — Data Fabric architecture
  9. rag-pipeline.png       — RAG pipeline (Docling → watsonx.ai, 8 stages)
  10. governance-triad.png  — Three governance layers with maturity bars

Usage:
    python deck/generate_diagrams.py
"""

from __future__ import annotations

import svgwrite
import cairosvg
from pathlib import Path

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "assets"

PAPER = "#F4F2EC"
GRID = "#E1DCCB"
ACCENT = "#2D4ADE"
ACCENT_LIGHT = "#E8F0FE"
INK = "#15171A"
INK2 = "#3A3F47"
SLATE = "#5C6470"
RULE = "#C9C4B6"
WHITE = "#FFFFFF"
WARN_YELLOW = "#F5A623"

W, H = 1920, 1080

FONT_MONO = "Consolas, monospace"
FONT_SANS = "Calibri, sans-serif"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _new_drawing(filename: str) -> svgwrite.Drawing:
    """Create a new SVG drawing with the standard canvas size."""
    path = str(OUTPUT_DIR / filename)
    dwg = svgwrite.Drawing(path, size=(f"{W}px", f"{H}px"), viewBox=f"0 0 {W} {H}")
    return dwg


def _draw_background(dwg: svgwrite.Drawing) -> None:
    """Paper background + blueprint grid."""
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=PAPER))
    for x in range(0, W + 1, 40):
        dwg.add(dwg.line(start=(x, 0), end=(x, H), stroke=GRID, stroke_width=0.5))
    for y in range(0, H + 1, 40):
        dwg.add(dwg.line(start=(0, y), end=(W, y), stroke=GRID, stroke_width=0.5))


def _draw_box(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = ACCENT_LIGHT,
    stroke: str = RULE,
    stroke_width: float = 1,
    rx: float = 4,
) -> None:
    """Draw a rounded rectangle."""
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), fill=fill, stroke=stroke, stroke_width=stroke_width, rx=rx, ry=rx))


def _draw_text(
    dwg: svgwrite.Drawing,
    text: str,
    x: float,
    y: float,
    font_size: float = 14,
    font_family: str = FONT_MONO,
    fill: str = INK,
    anchor: str = "start",
    weight: str = "normal",
) -> None:
    """Draw text at position."""
    dwg.add(
        dwg.text(
            text,
            insert=(x, y),
            font_size=f"{font_size}px",
            font_family=font_family,
            fill=fill,
            text_anchor=anchor,
            font_weight=weight,
        )
    )


def _draw_arrow(
    dwg: svgwrite.Drawing,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = INK2,
    width: float = 2,
) -> None:
    """Draw a line with an arrowhead."""
    marker = dwg.marker(insert=(6, 3), size=(8, 8), orient="auto")
    marker.add(dwg.polygon(points=[(0, 0), (6, 3), (0, 6)], fill=color))
    dwg.defs.add(marker)
    line = dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=width)
    line["marker-end"] = marker.get_funciri()
    dwg.add(line)


def _dim_overlay(dwg: svgwrite.Drawing, x: float, y: float, w: float, h: float) -> None:
    """Draw a white overlay at 70% opacity to dim a region to ~30%."""
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), fill=WHITE, opacity=0.7))


def _save(dwg: svgwrite.Drawing) -> None:
    """Save SVG and convert to PNG."""
    svg_path = dwg.filename
    png_path = svg_path.replace(".svg", ".png")
    dwg.save()
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=W, output_height=H)
    print(f"  {Path(png_path).name}")


def _draw_labeled_box(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    items: list[str] | None = None,
    fill: str = ACCENT_LIGHT,
    label_color: str = INK,
    item_color: str = INK2,
    font_size_label: float = 13,
    font_size_item: float = 11,
) -> None:
    """Box with a bold label and optional list of items inside."""
    _draw_box(dwg, x, y, w, h, fill=fill)
    _draw_text(dwg, label, x + 8, y + 18, font_size=font_size_label, fill=label_color, weight="bold")
    if items:
        for i, item in enumerate(items):
            _draw_text(dwg, item, x + 12, y + 34 + i * 15, font_size=font_size_item, fill=item_color)


def _draw_caution_icon(dwg: svgwrite.Drawing, cx: float, cy: float, size: float = 20) -> None:
    """Draw a triangular caution icon (triangle with !)."""
    half = size / 2
    points = [(cx, cy - half), (cx + half, cy + half), (cx - half, cy + half)]
    dwg.add(dwg.polygon(points=points, fill=WARN_YELLOW, stroke=INK, stroke_width=1.5))
    _draw_text(dwg, "!", cx, cy + half - 4, font_size=size * 0.7, anchor="middle", fill=INK, weight="bold")


# ===========================================================================
# REFERENCE ARCHITECTURE — shared drawing logic
# ===========================================================================

# Swimlane geometry: (label, x, y, w, h, items)
# We lay out the reference architecture in a structured way matching the PDF.

_DATA_SOURCES_ITEMS = [
    "Machine & Sensor Data",
    "Images & Video",
    "Content Services",
    "Social Data",
    "Internet Data Sets",
    "Weather Data",
    "Commercial Data Sets",
    "Third-Party Data",
    "Application Data",
    "Transactional Data",
    "System of Record Data",
]

_INGESTION_ITEMS = [
    "Data Replication",
    "Data Integration",
    "Data Intelligence",
    "Presto (connector)",
    "Connectivity",
]

_STORAGE_ON_HUB = [
    "watsonx.data",
    "Db2",
    "Db2 Warehouse (SMP, MPP)",
    "MongoDB",
    "EDB PostgreSQL",
    "Informix",
]

_STORAGE_OFF_HUB = [
    "Db2 for z/OS & i",
    "DataStax",
    "Denodo",
    "Dremio",
    "Oracle (& RDS)",
    "Teradata",
    "MS SQL Server",
    "MongoDB",
    "PostgreSQL/Netezza",
    "SingleStore",
    "Cloud Object Storage",
]

_DATA_ACCESS_ITEMS = [
    "Data Virtualization",
    "Apache Spark SQL",
    "Hadoop Execution Engine",
    "Iceberg / Delta Lake / Milvus",
    "Connectivity",
]

_ANALYTICS_MOTION = [
    "Apache Spark (Streaming)",
    "Apache Kafka",
]

_DISCOVERY_ITEMS = [
    "IBM Knowledge Catalog",
    "  Enterprise Search",
    "  Data Catalog",
    "  Data Refinery",
    "Watson Studio",
]

_ACTIONABLE_ITEMS = [
    "Watson Studio",
    "Watson OpenScale",
    "Watson Machine Learning",
    "Orchestration Pipelines",
    "SPSS Modeler",
    "Decision Optimization",
    "watsonx.ai",
    "Watson AI Services",
    "Cognos Dashboards",
    "Cognos Analytics",
    "Planning Analytics",
]

_BUSINESS_ITEMS = [
    "Customer Insights",
    "New Business Models",
    "Planning & Analysis",
    "Compliance & Fraud",
    "Security",
    "Operations",
]

_GOVERNANCE_ITEMS = [
    "Business Glossary",
    "Data Lineage",
    "Metadata Enrichment",
    "Governance Catalog",
    "Data Quality",
    "Model Inventory",
    "Regulatory Accelerators",
    "MDM/Match 360",
    "Data Privacy",
    "Product Master",
    "AI Factsheets",
    "watsonx.ai",
]

_SECURITY_ITEMS = [
    "Pre-integrated stack",
    "User roles & monitoring",
    "Industry certifications",
    "IBM Security",
    "Guardium Data Protection",
]

_DEPLOY_ITEMS = [
    "IBM Cloud",
    "AWS",
    "Azure",
    "Google Cloud",
    "On-Premise",
    "Red Hat OpenShift",
]


def _draw_refarch_core(dwg: svgwrite.Drawing) -> dict[str, tuple[float, float, float, float]]:
    """Draw the full reference architecture and return lane bounding boxes.

    Returns a dict mapping lane group names to (x, y, w, h) for overlay targeting.
    Groups: 'sources', 'acquisition', 'ingestion', 'storage', 'access',
            'analytics_motion', 'discovery', 'actionable', 'business',
            'governance', 'security', 'platform', 'deploy'
    """
    lanes: dict[str, tuple[float, float, float, float]] = {}

    # ---- Title ----
    _draw_text(
        dwg,
        "IBM Software Hub — Reference Architecture",
        W / 2,
        36,
        font_size=22,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )

    # ---- Layout constants ----
    left_col_x = 30
    left_col_w = 160
    acq_x = left_col_x + left_col_w + 8
    acq_w = 30
    center_x = acq_x + acq_w + 8
    center_w = 900
    right_x = center_x + center_w + 12
    right_w = W - right_x - 30
    top_y = 54

    # ---- Data Sources (left column) ----
    ds_h = 440
    _draw_labeled_box(dwg, left_col_x, top_y, left_col_w, ds_h, "Data Sources", _DATA_SOURCES_ITEMS, fill=ACCENT_LIGHT)
    lanes["sources"] = (left_col_x, top_y, left_col_w, ds_h)

    # ---- Data Acquisition & Application Access (vertical bar) ----
    _draw_box(dwg, acq_x, top_y, acq_w, ds_h, fill=ACCENT)
    _draw_text(dwg, "D", acq_x + 10, top_y + 80, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "a", acq_x + 10, top_y + 95, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "t", acq_x + 10, top_y + 110, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "a", acq_x + 10, top_y + 125, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, " ", acq_x + 10, top_y + 140, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "A", acq_x + 10, top_y + 160, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "c", acq_x + 10, top_y + 175, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "q", acq_x + 10, top_y + 190, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "u", acq_x + 10, top_y + 205, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "i", acq_x + 10, top_y + 220, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "s", acq_x + 10, top_y + 235, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "i", acq_x + 10, top_y + 250, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "t", acq_x + 10, top_y + 265, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "i", acq_x + 10, top_y + 280, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "o", acq_x + 10, top_y + 295, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    _draw_text(dwg, "n", acq_x + 10, top_y + 310, font_size=11, fill=WHITE, weight="bold", anchor="middle")
    lanes["acquisition"] = (acq_x, top_y, acq_w, ds_h)

    # ---- Ingestion & Integration (center top) ----
    ing_y = top_y
    ing_h = 100
    _draw_labeled_box(
        dwg, center_x, ing_y, center_w, ing_h, "Ingestion & Integration", _INGESTION_ITEMS, fill=ACCENT_LIGHT
    )
    lanes["ingestion"] = (center_x, ing_y, center_w, ing_h)

    # ---- Analytical Data Management & Storage ----
    stor_y = ing_y + ing_h + 8
    stor_h = 210
    _draw_box(dwg, center_x, stor_y, center_w, stor_h, fill=WHITE, stroke=RULE)
    _draw_text(
        dwg,
        "Analytical Data Management & Storage",
        center_x + 8,
        stor_y + 18,
        font_size=14,
        fill=INK,
        weight="bold",
    )
    # On-hub sub-box
    on_hub_x = center_x + 12
    on_hub_y = stor_y + 28
    on_hub_w = (center_w - 36) // 2
    on_hub_h = stor_h - 40
    _draw_labeled_box(
        dwg,
        on_hub_x,
        on_hub_y,
        on_hub_w,
        on_hub_h,
        "On Software Hub",
        _STORAGE_ON_HUB,
        fill=ACCENT_LIGHT,
    )
    # Off-hub sub-box
    off_hub_x = on_hub_x + on_hub_w + 12
    _draw_labeled_box(
        dwg,
        off_hub_x,
        on_hub_y,
        on_hub_w,
        on_hub_h,
        "Outside Software Hub",
        _STORAGE_OFF_HUB,
        fill="#F9F8F5",
        font_size_item=10,
    )
    lanes["storage"] = (center_x, stor_y, center_w, stor_h)

    # ---- Data Access ----
    acc_y = stor_y + stor_h + 8
    acc_h = 100
    _draw_labeled_box(dwg, center_x, acc_y, center_w, acc_h, "Data Access", _DATA_ACCESS_ITEMS, fill=ACCENT_LIGHT)
    lanes["access"] = (center_x, acc_y, center_w, acc_h)

    # ---- Analytics In-Motion ----
    aim_y = acc_y + acc_h + 8
    aim_h = 55
    _draw_labeled_box(
        dwg, center_x, aim_y, center_w, aim_h, "Analytics In-Motion", _ANALYTICS_MOTION, fill=ACCENT_LIGHT
    )
    lanes["analytics_motion"] = (center_x, aim_y, center_w, aim_h)

    # ---- Discovery & Exploration (right top) ----
    disc_y = top_y
    disc_h = 150
    _draw_labeled_box(
        dwg, right_x, disc_y, right_w, disc_h, "Discovery & Exploration", _DISCOVERY_ITEMS, fill=ACCENT_LIGHT
    )
    lanes["discovery"] = (right_x, disc_y, right_w, disc_h)

    # ---- Actionable Insight (right middle) ----
    act_y = disc_y + disc_h + 8
    act_h = 200
    _draw_labeled_box(dwg, right_x, act_y, right_w, act_h, "Actionable Insight", _ACTIONABLE_ITEMS, fill=ACCENT_LIGHT)
    lanes["actionable"] = (right_x, act_y, right_w, act_h)

    # ---- Business Process & Applications (right bottom) ----
    biz_y = act_y + act_h + 8
    biz_h = 125
    _draw_labeled_box(
        dwg,
        right_x,
        biz_y,
        right_w,
        biz_h,
        "Business Process & Applications",
        _BUSINESS_ITEMS,
        fill=ACCENT_LIGHT,
    )
    lanes["business"] = (right_x, biz_y, right_w, biz_h)

    # ---- Bottom bands (full width) ----
    band_x = 30
    band_w = W - 60
    band_gap = 6

    # Governance
    gov_y = aim_y + aim_h + 18
    gov_h = 75
    _draw_box(dwg, band_x, gov_y, band_w, gov_h, fill=ACCENT_LIGHT)
    _draw_text(
        dwg,
        "Information and Model Management & Governance",
        band_x + 10,
        gov_y + 18,
        font_size=13,
        fill=INK,
        weight="bold",
    )
    gov_items_text = " | ".join(_GOVERNANCE_ITEMS)
    # Split into two lines if needed
    mid = len(gov_items_text) // 2
    split_at = gov_items_text.index(" | ", mid)
    _draw_text(dwg, gov_items_text[:split_at], band_x + 14, gov_y + 38, font_size=10, fill=INK2)
    _draw_text(dwg, gov_items_text[split_at + 3 :], band_x + 14, gov_y + 54, font_size=10, fill=INK2)
    lanes["governance"] = (band_x, gov_y, band_w, gov_h)

    # Security
    sec_y = gov_y + gov_h + band_gap
    sec_h = 45
    _draw_box(dwg, band_x, sec_y, band_w, sec_h, fill=ACCENT_LIGHT)
    _draw_text(dwg, "Security", band_x + 10, sec_y + 18, font_size=13, fill=INK, weight="bold")
    sec_text = " | ".join(_SECURITY_ITEMS)
    _draw_text(dwg, sec_text, band_x + 14, sec_y + 35, font_size=10, fill=INK2)
    lanes["security"] = (band_x, sec_y, band_w, sec_h)

    # Platform
    plat_y = sec_y + sec_h + band_gap
    plat_h = 35
    _draw_box(dwg, band_x, plat_y, band_w, plat_h, fill=ACCENT)
    _draw_text(
        dwg,
        "IBM Software Hub (Cloud Pak for Data Platform)",
        band_x + 10,
        plat_y + 22,
        font_size=13,
        fill=WHITE,
        weight="bold",
    )
    lanes["platform"] = (band_x, plat_y, band_w, plat_h)

    # Deploy Anywhere
    dep_y = plat_y + plat_h + band_gap
    dep_h = 35
    _draw_box(dwg, band_x, dep_y, band_w, dep_h, fill="#F9F8F5")
    _draw_text(dwg, "Deploy Anywhere", band_x + 10, dep_y + 15, font_size=13, fill=INK, weight="bold")
    deploy_text = " | ".join(_DEPLOY_ITEMS)
    _draw_text(dwg, deploy_text, band_x + 180, dep_y + 15, font_size=11, fill=INK2)
    lanes["deploy"] = (band_x, dep_y, band_w, dep_h)

    # ---- Flow arrows between columns ----
    # Sources → Acquisition
    for offset in range(0, 400, 50):
        arr_y = top_y + 40 + offset
        if arr_y < top_y + ds_h - 10:
            _draw_arrow(dwg, left_col_x + left_col_w, arr_y, acq_x, arr_y, color=RULE, width=1)

    # Acquisition → Center
    for offset in range(0, 400, 60):
        arr_y = top_y + 50 + offset
        if arr_y < top_y + ds_h - 10:
            _draw_arrow(dwg, acq_x + acq_w, arr_y, center_x, arr_y, color=RULE, width=1)

    # Center → Right
    center_right_edge = center_x + center_w
    _draw_arrow(dwg, center_right_edge, top_y + 60, right_x, top_y + 60, color=RULE, width=1)
    _draw_arrow(dwg, center_right_edge, acc_y + 50, right_x, act_y + 50, color=RULE, width=1)

    return lanes


def _refarch_highlight_groups() -> dict[str, list[str]]:
    """Define which lane groups are highlighted in each block."""
    return {
        "block1": ["sources", "acquisition", "ingestion", "storage", "access"],
        "block2": ["analytics_motion", "discovery", "actionable", "business"],
        "block3": ["governance", "security", "platform", "deploy"],
    }


# ===========================================================================
# Diagram 1: refarch-full
# ===========================================================================
def _gen_refarch_full() -> None:
    dwg = _new_drawing("refarch-full.svg")
    _draw_background(dwg)
    _draw_refarch_core(dwg)
    _save(dwg)


# ===========================================================================
# Diagram 2: refarch-block1  (Storage + Access highlighted)
# ===========================================================================
def _gen_refarch_block1() -> None:
    dwg = _new_drawing("refarch-block1.svg")
    _draw_background(dwg)
    lanes = _draw_refarch_core(dwg)

    highlight_groups = _refarch_highlight_groups()
    highlighted = set(highlight_groups["block1"])

    for name, (x, y, w, h) in lanes.items():
        if name not in highlighted:
            _dim_overlay(dwg, x, y, w, h)

    _draw_text(
        dwg,
        "Block 1: Storage + Access Swimlanes",
        W / 2,
        H - 20,
        font_size=16,
        font_family=FONT_SANS,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )
    _save(dwg)


# ===========================================================================
# Diagram 3: refarch-block2  (AI/ingestion highlighted + gap callouts)
# ===========================================================================
def _gen_refarch_block2() -> None:
    dwg = _new_drawing("refarch-block2.svg")
    _draw_background(dwg)
    lanes = _draw_refarch_core(dwg)

    highlight_groups = _refarch_highlight_groups()
    highlighted = set(highlight_groups["block2"])

    for name, (x, y, w, h) in lanes.items():
        if name not in highlighted:
            _dim_overlay(dwg, x, y, w, h)

    # Docling gap callout
    callout_x = 80
    callout_y = H - 160
    _draw_box(dwg, callout_x, callout_y, 320, 60, fill=ACCENT, rx=6)
    _draw_text(dwg, "GAP: Docling (ingestion)", callout_x + 12, callout_y + 22, font_size=14, fill=WHITE, weight="bold")
    _draw_text(
        dwg,
        "Layout-aware extraction not in ref arch",
        callout_x + 12,
        callout_y + 44,
        font_size=12,
        fill=ACCENT_LIGHT,
    )
    # Arrow from callout to ingestion area
    ing = lanes["ingestion"]
    _draw_arrow(dwg, callout_x + 320, callout_y + 30, ing[0] + ing[2] / 2, ing[1] + ing[3], color=ACCENT, width=2)

    # Context Forge gap callout
    cf_x = 500
    cf_y = H - 160
    _draw_box(dwg, cf_x, cf_y, 360, 60, fill=ACCENT, rx=6)
    _draw_text(dwg, "GAP: MCP Context Forge", cf_x + 12, cf_y + 22, font_size=14, fill=WHITE, weight="bold")
    _draw_text(
        dwg,
        "Agent control plane not in ref arch",
        cf_x + 12,
        cf_y + 44,
        font_size=12,
        fill=ACCENT_LIGHT,
    )
    # Arrow to business lane
    biz = lanes["business"]
    _draw_arrow(dwg, cf_x + 360, cf_y + 10, biz[0] + biz[2] / 2, biz[1] + biz[3], color=ACCENT, width=2)

    _draw_text(
        dwg,
        "Block 2: AI / Ingestion Swimlanes + Gap Callouts",
        W / 2,
        H - 20,
        font_size=16,
        font_family=FONT_SANS,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )
    _save(dwg)


# ===========================================================================
# Diagram 4: refarch-block3  (Governance + Security + Deploy highlighted)
# ===========================================================================
def _gen_refarch_block3() -> None:
    dwg = _new_drawing("refarch-block3.svg")
    _draw_background(dwg)
    lanes = _draw_refarch_core(dwg)

    highlight_groups = _refarch_highlight_groups()
    highlighted = set(highlight_groups["block3"])

    for name, (x, y, w, h) in lanes.items():
        if name not in highlighted:
            _dim_overlay(dwg, x, y, w, h)

    _draw_text(
        dwg,
        "Block 3: Governance + Security + Deploy",
        W / 2,
        H - 20,
        font_size=16,
        font_family=FONT_SANS,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )
    _save(dwg)


# ===========================================================================
# Pattern diagrams — shared helpers
# ===========================================================================
def _draw_pattern_title(dwg: svgwrite.Drawing, title: str) -> None:
    _draw_text(dwg, title, W / 2, 56, font_size=28, font_family=FONT_SANS, fill=INK, anchor="middle", weight="bold")


def _draw_pattern_tagline(dwg: svgwrite.Drawing, tagline: str) -> None:
    _draw_text(
        dwg,
        tagline,
        W / 2,
        H - 40,
        font_size=18,
        font_family=FONT_SANS,
        fill=SLATE,
        anchor="middle",
    )


def _draw_source_column(dwg: svgwrite.Drawing, x: float, y: float, items: list[str]) -> float:
    """Draw source boxes in a column, return bottom y."""
    _draw_text(dwg, "Sources", x + 60, y - 10, font_size=16, fill=INK, anchor="middle", weight="bold")
    for i, item in enumerate(items):
        by = y + i * 55
        _draw_box(dwg, x, by, 140, 44, fill=ACCENT_LIGHT)
        _draw_text(dwg, item, x + 10, by + 27, font_size=12, fill=INK2)
    return y + len(items) * 55


def _draw_consumer_column(dwg: svgwrite.Drawing, x: float, y: float, items: list[str]) -> float:
    """Draw consumer boxes in a column."""
    _draw_text(dwg, "Consumers", x + 60, y - 10, font_size=16, fill=INK, anchor="middle", weight="bold")
    for i, item in enumerate(items):
        by = y + i * 55
        _draw_box(dwg, x, by, 140, 44, fill=ACCENT_LIGHT)
        _draw_text(dwg, item, x + 10, by + 27, font_size=12, fill=INK2)
    return y + len(items) * 55


def _draw_trait_line(dwg: svgwrite.Drawing, x: float, y: float, traits: list[str], good: bool = True) -> None:
    """Draw a row of traits with check or x marks."""
    prefix = "\u2713 " if good else "\u2717 "
    color = ACCENT if good else "#B5442D"
    for i, trait in enumerate(traits):
        tx = x + i * 260
        _draw_text(dwg, prefix + trait, tx, y, font_size=14, fill=color)


# ===========================================================================
# Diagram 5: pattern-lake
# ===========================================================================
def _gen_pattern_lake() -> None:
    dwg = _new_drawing("pattern-lake.svg")
    _draw_background(dwg)
    _draw_pattern_title(dwg, "DATA LAKE")

    sources = ["Core Banking", "CRM", "PDFs", "Streams"]
    consumers = ["Spark ML", "DuckDB", "Presto"]

    src_x, src_y = 120, 160
    _draw_source_column(dwg, src_x, src_y, sources)

    # Object storage (center, highlighted)
    stor_x, stor_y, stor_w, stor_h = 500, 120, 900, 460
    _draw_box(dwg, stor_x, stor_y, stor_w, stor_h, fill=ACCENT_LIGHT, stroke=ACCENT, stroke_width=2)
    _draw_text(
        dwg,
        "Object Storage",
        stor_x + stor_w / 2,
        stor_y + 36,
        font_size=20,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )
    _draw_text(
        dwg, "Bronze / Silver / Gold Zones", stor_x + stor_w / 2, stor_y + 64, font_size=16, fill=INK2, anchor="middle"
    )

    # File format boxes inside storage
    formats = ["Parquet", "JSON", "CSV", "Raw Files", "Images", "Logs"]
    for i, fmt in enumerate(formats):
        col = i % 3
        row = i // 3
        fx = stor_x + 100 + col * 260
        fy = stor_y + 100 + row * 110
        _draw_box(dwg, fx, fy, 220, 80, fill=WHITE)
        _draw_text(dwg, fmt, fx + 110, fy + 45, font_size=16, fill=INK2, anchor="middle")

    # "Any format, no schema" label
    _draw_text(
        dwg,
        "Schema-on-read. Any format accepted.",
        stor_x + stor_w / 2,
        stor_y + stor_h - 30,
        font_size=14,
        fill=SLATE,
        anchor="middle",
    )

    # Consumers
    cons_x = stor_x + stor_w + 80
    _draw_consumer_column(dwg, cons_x, 200, consumers)

    # Arrows: sources → storage
    for i in range(len(sources)):
        ay = src_y + i * 55 + 22
        _draw_arrow(dwg, src_x + 140, ay, stor_x, ay, color=ACCENT, width=2)

    # Arrows: storage → consumers
    for i in range(len(consumers)):
        ay = 200 + i * 55 + 22
        _draw_arrow(dwg, stor_x + stor_w, ay, cons_x, ay, color=ACCENT, width=2)

    # Traits
    ty = 680
    _draw_trait_line(dwg, 140, ty, ["Cheap storage", "Any format", "ML-friendly"], good=True)
    _draw_trait_line(dwg, 140, ty + 35, ["No ACID", "No schema enforcement", "No governance"], good=False)

    _draw_pattern_tagline(dwg, '"Schema-on-read. When (and if) someone reads it."')
    _save(dwg)


# ===========================================================================
# Diagram 6: pattern-lakehouse
# ===========================================================================
def _gen_pattern_lakehouse() -> None:
    dwg = _new_drawing("pattern-lakehouse.svg")
    _draw_background(dwg)
    _draw_pattern_title(dwg, "LAKEHOUSE")

    sources = ["Core Banking", "CRM", "PDFs", "Streams"]
    consumers = ["SQL / BI", "Spark ML", "Presto"]

    src_x, src_y = 100, 160
    _draw_source_column(dwg, src_x, src_y, sources)

    # Storage layer (center)
    stor_x, stor_y, stor_w, stor_h = 460, 120, 700, 520
    _draw_box(dwg, stor_x, stor_y, stor_w, stor_h, fill=ACCENT_LIGHT, stroke=RULE)
    _draw_text(
        dwg,
        "Object Storage + Open Table Format",
        stor_x + stor_w / 2,
        stor_y + 32,
        font_size=18,
        fill=INK,
        anchor="middle",
        weight="bold",
    )

    # Parquet files background
    pq_x, pq_y, pq_w, pq_h = stor_x + 40, stor_y + 50, stor_w - 80, 200
    _draw_box(dwg, pq_x, pq_y, pq_w, pq_h, fill=WHITE)
    _draw_text(dwg, "Parquet Files", pq_x + 20, pq_y + 30, font_size=14, fill=INK2)

    # ICEBERG box (highlighted — key differentiator)
    ice_x, ice_y, ice_w, ice_h = pq_x + 40, pq_y + 50, pq_w - 80, 130
    _draw_box(dwg, ice_x, ice_y, ice_w, ice_h, fill=ACCENT, stroke=ACCENT, stroke_width=2)
    _draw_text(
        dwg, "APACHE ICEBERG", ice_x + ice_w / 2, ice_y + 30, font_size=20, fill=WHITE, anchor="middle", weight="bold"
    )
    iceberg_features = ["ACID Transactions", "Schema Evolution", "Time Travel", "Partition Pruning"]
    for i, feat in enumerate(iceberg_features):
        _draw_text(
            dwg,
            feat,
            ice_x + 30 + (i % 2) * 260,
            ice_y + 60 + (i // 2) * 30,
            font_size=14,
            fill=ACCENT_LIGHT,
        )

    # Catalog box
    cat_x, cat_y, cat_w, cat_h = stor_x + 80, stor_y + 320, 300, 100
    _draw_box(dwg, cat_x, cat_y, cat_w, cat_h, fill=ACCENT_LIGHT, stroke=ACCENT)
    _draw_text(dwg, "Catalog", cat_x + 150, cat_y + 28, font_size=16, fill=ACCENT, anchor="middle", weight="bold")
    _draw_text(dwg, "Iceberg Catalog +", cat_x + 150, cat_y + 52, font_size=13, fill=INK2, anchor="middle")
    _draw_text(dwg, "Knowledge Catalog", cat_x + 150, cat_y + 70, font_size=13, fill=INK2, anchor="middle")

    # Governance box
    gov_x = cat_x + cat_w + 40
    _draw_box(dwg, gov_x, cat_y, 280, 100, fill=ACCENT_LIGHT, stroke=ACCENT)
    _draw_text(dwg, "Governance", gov_x + 140, cat_y + 28, font_size=16, fill=ACCENT, anchor="middle", weight="bold")
    _draw_text(dwg, "Lineage + Quality +", gov_x + 140, cat_y + 52, font_size=13, fill=INK2, anchor="middle")
    _draw_text(dwg, "Access Control", gov_x + 140, cat_y + 70, font_size=13, fill=INK2, anchor="middle")

    # Consumers
    cons_x = stor_x + stor_w + 80
    _draw_consumer_column(dwg, cons_x, 200, consumers)

    # Arrows
    for i in range(len(sources)):
        ay = src_y + i * 55 + 22
        _draw_arrow(dwg, src_x + 140, ay, stor_x, ay, color=ACCENT, width=2)
    for i in range(len(consumers)):
        ay = 200 + i * 55 + 22
        _draw_arrow(dwg, stor_x + stor_w, ay, cons_x, ay, color=ACCENT, width=2)

    # Traits
    ty = 720
    _draw_trait_line(dwg, 140, ty, ["ACID", "Schema evolution", "Time travel"], good=True)
    _draw_trait_line(dwg, 140, ty + 30, ["Open format (Iceberg/Delta)"], good=True)

    _draw_pattern_tagline(dwg, '"Warehouse semantics on lake economics."')
    _save(dwg)


# ===========================================================================
# Diagram 7: pattern-mesh
# ===========================================================================
def _gen_pattern_mesh() -> None:
    dwg = _new_drawing("pattern-mesh.svg")
    _draw_background(dwg)
    _draw_pattern_title(dwg, "DATA MESH")

    # Domain boxes
    domains = [
        ("Retail Domain", ["Lakehouse + Catalog", "Data Products", "SLAs + Ownership"]),
        ("Commercial Domain", ["Lakehouse + Catalog", "Data Products", "SLAs + Ownership"]),
        ("Risk Domain", ["Lakehouse + Catalog", "Data Products", "SLAs + Ownership"]),
    ]

    domain_w, domain_h = 460, 300
    domain_y = 100
    gap = 40
    total_w = len(domains) * domain_w + (len(domains) - 1) * gap
    start_x = (W - total_w) / 2

    for i, (name, items) in enumerate(domains):
        dx = start_x + i * (domain_w + gap)

        # Domain container
        _draw_box(dwg, dx, domain_y, domain_w, domain_h, fill=WHITE, stroke=ACCENT, stroke_width=2, rx=8)
        _draw_text(
            dwg, name, dx + domain_w / 2, domain_y + 30, font_size=18, fill=ACCENT, anchor="middle", weight="bold"
        )

        # Inner boxes
        # Lakehouse
        lh_x, lh_y = dx + 30, domain_y + 50
        _draw_box(dwg, lh_x, lh_y, domain_w - 60, 80, fill=ACCENT_LIGHT)
        _draw_text(
            dwg, "Lakehouse + Catalog", lh_x + (domain_w - 60) / 2, lh_y + 35, font_size=14, fill=INK, anchor="middle"
        )
        _draw_text(
            dwg,
            "Iceberg tables, local catalog",
            lh_x + (domain_w - 60) / 2,
            lh_y + 55,
            font_size=11,
            fill=SLATE,
            anchor="middle",
        )

        # Data Products
        dp_x, dp_y = dx + 30, domain_y + 150
        _draw_box(dwg, dp_x, dp_y, domain_w - 60, 80, fill=ACCENT_LIGHT, stroke=ACCENT)
        _draw_text(
            dwg,
            "Data Products",
            dp_x + (domain_w - 60) / 2,
            dp_y + 30,
            font_size=14,
            fill=ACCENT,
            anchor="middle",
            weight="bold",
        )
        _draw_text(
            dwg,
            "SLAs + Owner + Schema Contract",
            dp_x + (domain_w - 60) / 2,
            dp_y + 55,
            font_size=11,
            fill=SLATE,
            anchor="middle",
        )

    # Contract arrows between domains
    for i in range(len(domains) - 1):
        x1 = start_x + i * (domain_w + gap) + domain_w
        x2 = start_x + (i + 1) * (domain_w + gap)
        ay = domain_y + domain_h / 2
        _draw_arrow(dwg, x1, ay, x2, ay, color=ACCENT, width=2)
        _draw_arrow(dwg, x2, ay + 10, x1, ay + 10, color=ACCENT, width=2)
        _draw_text(dwg, "contracts", (x1 + x2) / 2, ay - 10, font_size=11, fill=ACCENT, anchor="middle")

    # Platform team band
    plat_y = domain_y + domain_h + 50
    plat_h = 100
    plat_x = start_x - 20
    plat_w = total_w + 40
    _draw_box(dwg, plat_x, plat_y, plat_w, plat_h, fill=ACCENT, rx=8)
    _draw_text(
        dwg,
        "Platform Team",
        plat_x + plat_w / 2,
        plat_y + 30,
        font_size=20,
        fill=WHITE,
        anchor="middle",
        weight="bold",
    )
    plat_items = ["Federated Catalog", "Governance Policies", "Observability", "Self-serve Infrastructure"]
    for i, item in enumerate(plat_items):
        _draw_text(
            dwg,
            item,
            plat_x + 80 + i * (plat_w - 160) / (len(plat_items) - 1),
            plat_y + 60,
            font_size=13,
            fill=ACCENT_LIGHT,
            anchor="middle",
        )

    # Arrows from domains to platform
    for i in range(len(domains)):
        dx = start_x + i * (domain_w + gap) + domain_w / 2
        _draw_arrow(dwg, dx, domain_y + domain_h, dx, plat_y, color=RULE, width=1)

    # Key principle callout
    _draw_box(dwg, start_x, plat_y + plat_h + 30, plat_w, 60, fill=ACCENT_LIGHT, rx=6)
    _draw_text(
        dwg,
        "Key Principle: Domain teams own their data as a product. Platform enables, does not centralize.",
        plat_x + plat_w / 2,
        plat_y + plat_h + 65,
        font_size=15,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )

    _draw_pattern_tagline(dwg, '"An org change, expressed in YAML."')
    _save(dwg)


# ===========================================================================
# Diagram 8: pattern-fabric
# ===========================================================================
def _gen_pattern_fabric() -> None:
    dwg = _new_drawing("pattern-fabric.svg")
    _draw_background(dwg)
    _draw_pattern_title(dwg, "DATA FABRIC")

    # Metadata + AI automation layer (top, highlighted — key differentiator)
    meta_x, meta_y, meta_w, meta_h = 120, 100, W - 240, 200
    _draw_box(dwg, meta_x, meta_y, meta_w, meta_h, fill=ACCENT, stroke=ACCENT, stroke_width=2, rx=8)
    _draw_text(
        dwg,
        "METADATA + AI AUTOMATION",
        meta_x + meta_w / 2,
        meta_y + 35,
        font_size=22,
        fill=WHITE,
        anchor="middle",
        weight="bold",
    )
    meta_items = [
        "Knowledge Graph",
        "Auto-classification",
        "Policy Engine",
        "Automated Lineage",
        "Self-serve Discovery",
    ]
    for i, item in enumerate(meta_items):
        ix = meta_x + 80 + i * (meta_w - 160) / (len(meta_items) - 1)
        _draw_box(dwg, ix - 85, meta_y + 60, 170, 50, fill="#1A3AB5", rx=4)
        _draw_text(dwg, item, ix, meta_y + 90, font_size=13, fill=WHITE, anchor="middle")

    # Connector lines from metadata layer down
    data_stores = [
        ("Warehouse (Db2)", 220, ACCENT_LIGHT),
        ("Lakehouse (Iceberg)", 580, ACCENT_LIGHT),
        ("Data Lake (MinIO)", 940, ACCENT_LIGHT),
        ("External DBs (Oracle, SQL)", 1300, "#F9F8F5"),
        ("Cloud Services (S3)", 1560, "#F9F8F5"),
    ]

    store_y = meta_y + meta_h + 80
    store_h = 180
    store_w = 260

    for label, cx, fill in data_stores:
        sx = cx - store_w / 2
        _draw_box(dwg, sx, store_y, store_w, store_h, fill=fill, stroke=RULE)
        _draw_text(dwg, label, cx, store_y + 30, font_size=14, fill=INK, anchor="middle", weight="bold")

        # Sample contents
        inner_items = ["Tables", "Files", "Views"]
        for j, inner in enumerate(inner_items):
            _draw_box(dwg, sx + 20, store_y + 50 + j * 38, store_w - 40, 30, fill=WHITE, rx=3)
            _draw_text(dwg, inner, cx, store_y + 70 + j * 38, font_size=11, fill=INK2, anchor="middle")

        # Arrow from metadata layer to store
        _draw_arrow(dwg, cx, meta_y + meta_h, cx, store_y, color=ACCENT, width=2)

    # Consumers at bottom
    cons_y = store_y + store_h + 60
    cons_h = 80
    _draw_box(dwg, 120, cons_y, W - 240, cons_h, fill=ACCENT_LIGHT, rx=8)
    _draw_text(
        dwg,
        "Data Consumers",
        W / 2,
        cons_y + 25,
        font_size=18,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    consumers = ["Analysts (self-serve)", "ML Engineers", "Applications", "Compliance / Audit"]
    for i, cons in enumerate(consumers):
        _draw_text(
            dwg,
            cons,
            200 + i * 400,
            cons_y + 55,
            font_size=14,
            fill=INK2,
            anchor="middle",
        )

    # Traits
    ty = cons_y + cons_h + 40
    _draw_trait_line(dwg, 180, ty, ["Spans heterogeneous estates", "AI-driven governance"], good=True)
    _draw_trait_line(dwg, 180, ty + 30, ["Automated discovery + lineage", "Self-serve for consumers"], good=True)

    _draw_pattern_tagline(dwg, '"The metadata layer that knows where everything is."')
    _save(dwg)


# ===========================================================================
# Diagram 9: rag-pipeline
# ===========================================================================
def _gen_rag_pipeline() -> None:
    dwg = _new_drawing("rag-pipeline.svg")
    _draw_background(dwg)
    _draw_text(
        dwg,
        "RAG Pipeline: Docling \u2192 watsonx.ai",
        W / 2,
        50,
        font_size=26,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )

    stages = [
        ("Policy\nPDFs", "10 PDFs\n~300 pages"),
        ("Docling\n(parse)", "Layout-aware\nmarkdown"),
        ("Section-\naware\nchunking", "##/### split\n~600 chunks"),
        ("sentence-\ntransformers\n(embed)", "384-dim vectors\nall-MiniLM-L6"),
        ("OpenSearch\nkNN +\nBM25", "Hybrid\nretrieval"),
        ("Reranker\n(cross-\nencoder)", "Precision\ntop-k rerank"),
        ("Context\nAssembly", "Window\nassembly"),
        ("watsonx.ai\n(generate)", "Response +\nprovenance"),
    ]

    n = len(stages)
    box_w = 170
    box_h = 130
    gap = 18
    total_w = n * box_w + (n - 1) * gap
    start_x = (W - total_w) / 2
    box_y = 180

    caution_stages = {2, 4}  # Chunking and retrieval (0-indexed)

    for i, (label, detail) in enumerate(stages):
        bx = start_x + i * (box_w + gap)
        fill = ACCENT if i in (1, 7) else ACCENT_LIGHT  # Highlight Docling and watsonx.ai
        text_fill = WHITE if i in (1, 7) else INK

        _draw_box(
            dwg,
            bx,
            box_y,
            box_w,
            box_h,
            fill=fill,
            stroke=ACCENT if i in (1, 7) else RULE,
            stroke_width=2 if i in (1, 7) else 1,
            rx=6,
        )

        # Multi-line label
        lines = label.split("\n")
        for j, line in enumerate(lines):
            _draw_text(
                dwg,
                line,
                bx + box_w / 2,
                box_y + 30 + j * 20,
                font_size=14 if j == 0 else 12,
                fill=text_fill,
                anchor="middle",
                weight="bold" if j == 0 else "normal",
            )

        # Details below box
        detail_lines = detail.split("\n")
        for j, dline in enumerate(detail_lines):
            _draw_text(
                dwg,
                dline,
                bx + box_w / 2,
                box_y + box_h + 25 + j * 18,
                font_size=11,
                fill=SLATE,
                anchor="middle",
            )

        # Arrow to next stage
        if i < n - 1:
            _draw_arrow(
                dwg,
                bx + box_w,
                box_y + box_h / 2,
                bx + box_w + gap,
                box_y + box_h / 2,
                color=ACCENT,
                width=2,
            )

        # Caution icon at failure-prone stages
        if i in caution_stages:
            _draw_caution_icon(dwg, bx + box_w / 2, box_y - 18, size=24)

    # Caution legend
    legend_y = box_y + box_h + 100
    _draw_caution_icon(dwg, 200, legend_y, size=20)
    _draw_text(
        dwg,
        "= Known failure point in production",
        225,
        legend_y + 6,
        font_size=13,
        fill=SLATE,
    )

    # Stage numbers at top
    _draw_text(
        dwg,
        "8 stages: Ingest \u2192 Parse \u2192 Chunk \u2192 Embed \u2192 Retrieve \u2192 Rerank \u2192 Assemble \u2192 Generate",
        W / 2,
        140,
        font_size=15,
        fill=INK2,
        anchor="middle",
        font_family=FONT_SANS,
    )

    # "Maple Trust Bank" label
    _draw_text(
        dwg,
        "Implementation: Maple Trust Bank AML Policy Q&A",
        W / 2,
        H - 30,
        font_size=15,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
    )
    _save(dwg)


# ===========================================================================
# Diagram 10: governance-triad
# ===========================================================================
def _gen_governance_triad() -> None:
    dwg = _new_drawing("governance-triad.svg")
    _draw_background(dwg)
    _draw_text(
        dwg,
        "Three Governance Layers",
        W / 2,
        50,
        font_size=26,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )

    bands = [
        {
            "title": "DATA GOVERNANCE",
            "maturity": "MATURE",
            "filled": 4,
            "total": 4,
            "capabilities": "Lineage \u00b7 Quality \u00b7 Access \u00b7 Classification \u00b7 Lifecycle",
            "tools": "Tools: Knowledge Catalog, OpenLineage, Great Expectations",
            "fill": ACCENT,
        },
        {
            "title": "AI / MODEL GOVERNANCE",
            "maturity": "EMERGING",
            "filled": 3,
            "total": 4,
            "capabilities": "Model cards \u00b7 Bias \u00b7 Drift \u00b7 E-23 \u00b7 SR 11-7 \u00b7 Factsheets",
            "tools": "Tools: watsonx.governance, MLflow, Weights & Biases",
            "fill": "#1A3AB5",
        },
        {
            "title": "AGENT GOVERNANCE",
            "maturity": "NEW",
            "filled": 1,
            "total": 4,
            "capabilities": "NHI \u00b7 Blast radius \u00b7 Kill switch \u00b7 Tool audit \u00b7 Prompt injection",
            "tools": "Tools: Context Forge, (almost nothing else)",
            "fill": "#5B73E8",
        },
    ]

    band_x = 80
    band_w = W - 160
    band_h = 200
    band_gap = 30
    start_y = 100

    for i, band in enumerate(bands):
        by = start_y + i * (band_h + band_gap)

        # Band background
        _draw_box(dwg, band_x, by, band_w, band_h, fill=band["fill"], rx=10, stroke=band["fill"], stroke_width=2)

        # Title
        _draw_text(dwg, band["title"], band_x + 30, by + 38, font_size=24, fill=WHITE, weight="bold")

        # Maturity label + bar
        bar_x = band_x + band_w - 350
        _draw_text(dwg, band["maturity"], bar_x, by + 38, font_size=18, fill=ACCENT_LIGHT, weight="bold")

        bar_block_w = 40
        bar_block_h = 28
        bar_block_gap = 6
        bar_start_x = bar_x + 160
        bar_y = by + 16
        for j in range(band["total"]):
            bx = bar_start_x + j * (bar_block_w + bar_block_gap)
            if j < band["filled"]:
                _draw_box(dwg, bx, bar_y, bar_block_w, bar_block_h, fill=WHITE, stroke=WHITE, stroke_width=1, rx=3)
            else:
                # Empty block: white with low opacity
                r = dwg.rect(
                    insert=(bx, bar_y),
                    size=(bar_block_w, bar_block_h),
                    fill=WHITE,
                    stroke=WHITE,
                    stroke_width=1,
                    rx=3,
                    ry=3,
                )
                r["opacity"] = 0.2
                dwg.add(r)

        # Capabilities
        _draw_text(dwg, band["capabilities"], band_x + 30, by + 80, font_size=16, fill=ACCENT_LIGHT)

        # Tools (semi-transparent white text)
        t = dwg.text(
            band["tools"],
            insert=(band_x + 30, by + 115),
            font_size="14px",
            font_family=FONT_MONO,
            fill=WHITE,
            opacity=0.8,
        )
        dwg.add(t)

        # Additional context line for agent governance
        if i == 2:
            _draw_text(
                dwg,
                "The gap is here. This is why agents are a governance problem, not just an AI problem.",
                band_x + 30,
                by + 150,
                font_size=15,
                fill=WARN_YELLOW,
                weight="bold",
            )

    # Arrow annotation showing the gap
    arrow_y = start_y + 2 * (band_h + band_gap) + band_h + 20
    _draw_text(
        dwg,
        "\u2191 Maturity decreases. Urgency increases. \u2191",
        W / 2,
        arrow_y,
        font_size=18,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
        font_family=FONT_SANS,
    )

    _save(dwg)


# ===========================================================================
# Main
# ===========================================================================
def main() -> None:
    _ensure_output_dir()
    print("Generating diagrams...")

    _gen_refarch_full()
    _gen_refarch_block1()
    _gen_refarch_block2()
    _gen_refarch_block3()
    _gen_pattern_lake()
    _gen_pattern_lakehouse()
    _gen_pattern_mesh()
    _gen_pattern_fabric()
    _gen_rag_pipeline()
    _gen_governance_triad()

    print(f"\nDone. {len(list(OUTPUT_DIR.glob('*.png')))} PNGs in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
