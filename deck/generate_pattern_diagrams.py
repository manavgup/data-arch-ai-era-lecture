#!/usr/bin/env python3
"""Generate 5 SVG pattern diagrams matching the data-arch-ai-era-lecture style.

Produces:
  1. pattern-warehouse.svg/.png
  2. pattern-lake.svg/.png
  3. pattern-lakehouse.svg/.png
  4. pattern-fabric.svg/.png
  5. pattern-mesh.svg/.png

Uses the IBM Software Hub component vocabulary and the lecture's design tokens
(paper background, blueprint grid, accent blue, monospace labels).

Usage:
    python generate_pattern_diagrams.py
"""

from __future__ import annotations

import svgwrite
import cairosvg
from pathlib import Path

# ---------------------------------------------------------------------------
# Design tokens (matching data-arch-ai-era-lecture/deck/generate_diagrams.py)
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "assets"

PAPER = "#F4F2EC"
GRID = "#E1DCCB"
ACCENT = "#2D4ADE"
ACCENT_LIGHT = "#E8F0FE"
ACCENT_DEEP = "#1A3AB5"
INK = "#15171A"
INK2 = "#3A3F47"
SLATE = "#5C6470"
RULE = "#C9C4B6"
WHITE = "#FFFFFF"
WARN = "#F5A623"
DIM_FILL = "#F9F8F5"
GOOD = "#2D4ADE"
BAD = "#B5442D"

W, H = 1920, 1080

FONT_MONO = "Consolas, Menlo, monospace"
FONT_SANS = "Calibri, Helvetica, Arial, sans-serif"


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def _ensure_output() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _new_drawing(filename: str) -> svgwrite.Drawing:
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


def _box(
    dwg,
    x,
    y,
    w,
    h,
    fill=ACCENT_LIGHT,
    stroke=RULE,
    stroke_width=1,
    rx=4,
):
    dwg.add(
        dwg.rect(
            insert=(x, y),
            size=(w, h),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            rx=rx,
            ry=rx,
        )
    )


def _text(
    dwg,
    text,
    x,
    y,
    font_size=14,
    font_family=FONT_MONO,
    fill=INK,
    anchor="start",
    weight="normal",
):
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


def _arrow(dwg, x1, y1, x2, y2, color=INK2, width=2, marker_id=None):
    """Line with arrowhead. Each arrow needs its own marker for color."""
    if marker_id is None:
        marker_id = f"arr-{id((x1, y1, x2, y2, color))}"
    marker = dwg.marker(id=marker_id, insert=(6, 3), size=(8, 8), orient="auto")
    marker.add(dwg.polygon(points=[(0, 0), (6, 3), (0, 6)], fill=color))
    dwg.defs.add(marker)
    line = dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=width)
    line["marker-end"] = marker.get_funciri()
    dwg.add(line)


def _labeled_box(
    dwg,
    x,
    y,
    w,
    h,
    label,
    items=None,
    fill=ACCENT_LIGHT,
    label_color=INK,
    item_color=INK2,
    font_size_label=13,
    font_size_item=11,
    stroke=RULE,
    stroke_width=1,
):
    _box(dwg, x, y, w, h, fill=fill, stroke=stroke, stroke_width=stroke_width)
    _text(dwg, label, x + 10, y + 22, font_size=font_size_label, fill=label_color, weight="bold")
    if items:
        for i, item in enumerate(items):
            _text(dwg, item, x + 14, y + 42 + i * 16, font_size=font_size_item, fill=item_color)


def _save(dwg: svgwrite.Drawing) -> None:
    """Save SVG and rasterize to PNG."""
    svg_path = dwg.filename
    png_path = svg_path.replace(".svg", ".png")
    dwg.save()
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=W, output_height=H)
    print(f"  {Path(png_path).name}")


# ---------------------------------------------------------------------------
# Common building blocks
# ---------------------------------------------------------------------------
def _draw_title(dwg: svgwrite.Drawing, title: str, subtitle: str = "") -> None:
    _text(
        dwg,
        title,
        W / 2,
        56,
        font_size=32,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    if subtitle:
        _text(
            dwg,
            subtitle,
            W / 2,
            92,
            font_size=18,
            font_family=FONT_SANS,
            fill=SLATE,
            anchor="middle",
        )


def _draw_tagline(dwg: svgwrite.Drawing, tagline: str) -> None:
    _text(
        dwg,
        tagline,
        W / 2,
        H - 40,
        font_size=20,
        font_family=FONT_SANS,
        fill=SLATE,
        anchor="middle",
    )


def _draw_traits(dwg, x, y, good_traits, bad_traits=None):
    """Draw rows of pros / cons."""
    for i, trait in enumerate(good_traits):
        col = i % 3
        row = i // 3
        tx = x + col * 360
        ty = y + row * 30
        _text(dwg, "\u2713 " + trait, tx, ty, font_size=15, fill=GOOD, weight="bold")
    if bad_traits:
        offset_y = y + 30 * ((len(good_traits) + 2) // 3) + 10
        for i, trait in enumerate(bad_traits):
            col = i % 3
            row = i // 3
            tx = x + col * 360
            ty = offset_y + row * 30
            _text(dwg, "\u2717 " + trait, tx, ty, font_size=15, fill=BAD, weight="bold")


def _draw_source_column(dwg, x, y, items, label="Sources"):
    """Vertical stack of source boxes."""
    _text(
        dwg,
        label,
        x + 80,
        y - 16,
        font_size=18,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    box_h = 48
    box_gap = 12
    for i, item in enumerate(items):
        by = y + i * (box_h + box_gap)
        _box(dwg, x, by, 160, box_h, fill=ACCENT_LIGHT)
        _text(dwg, item, x + 12, by + 30, font_size=12, fill=INK2)
    return y + len(items) * (box_h + box_gap)


def _draw_consumer_column(dwg, x, y, items, label="Consumers"):
    _text(
        dwg,
        label,
        x + 80,
        y - 16,
        font_size=18,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    box_h = 48
    box_gap = 12
    for i, item in enumerate(items):
        by = y + i * (box_h + box_gap)
        _box(dwg, x, by, 160, box_h, fill=ACCENT_LIGHT)
        _text(dwg, item, x + 12, by + 30, font_size=12, fill=INK2)
    return y + len(items) * (box_h + box_gap)


# ===========================================================================
# Pattern 1: Data Warehouse
# ===========================================================================
def gen_warehouse() -> None:
    dwg = _new_drawing("pattern-warehouse.svg")
    _draw_background(dwg)
    _draw_title(dwg, "DATA WAREHOUSE", "Schema-on-write. Curated relational store for governed BI.")

    sources = ["Core Banking", "ERP", "CRM", "System of Record"]
    consumers = ["Cognos BI", "Reports", "Planning"]

    src_x, src_y = 90, 240
    _draw_source_column(dwg, src_x, src_y, sources)

    # ETL stage
    etl_x, etl_y, etl_w, etl_h = 320, 280, 220, 320
    _box(dwg, etl_x, etl_y, etl_w, etl_h, fill=ACCENT_LIGHT, stroke=RULE)
    _text(
        dwg,
        "ETL",
        etl_x + etl_w / 2,
        etl_y + 36,
        font_size=22,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    _text(
        dwg,
        "Transform on write",
        etl_x + etl_w / 2,
        etl_y + 64,
        font_size=14,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
    )
    etl_items = ["DataStage", "Data Replication", "Data Integration"]
    for i, item in enumerate(etl_items):
        _box(dwg, etl_x + 24, etl_y + 100 + i * 60, etl_w - 48, 48, fill=WHITE)
        _text(
            dwg,
            item,
            etl_x + etl_w / 2,
            etl_y + 130 + i * 60,
            font_size=14,
            fill=INK2,
            anchor="middle",
            weight="bold",
        )

    # Curated warehouse (center, highlighted)
    wh_x, wh_y, wh_w, wh_h = 620, 200, 720, 480
    _box(dwg, wh_x, wh_y, wh_w, wh_h, fill=ACCENT_LIGHT, stroke=ACCENT, stroke_width=3)
    _text(
        dwg,
        "Db2 Warehouse",
        wh_x + wh_w / 2,
        wh_y + 50,
        font_size=28,
        font_family=FONT_SANS,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )
    _text(
        dwg,
        "Conformed dimensional models",
        wh_x + wh_w / 2,
        wh_y + 84,
        font_size=16,
        fill=INK2,
        anchor="middle",
        font_family=FONT_SANS,
    )

    # Star schema icon
    cx, cy = wh_x + wh_w / 2, wh_y + 280
    fact_w, fact_h = 200, 80
    _box(dwg, cx - fact_w / 2, cy - fact_h / 2, fact_w, fact_h, fill=ACCENT, rx=6)
    _text(
        dwg,
        "FACT",
        cx,
        cy + 6,
        font_size=22,
        fill=WHITE,
        anchor="middle",
        weight="bold",
        font_family=FONT_SANS,
    )

    dim_offset = 200
    dim_w, dim_h = 140, 56
    dim_positions = [
        (cx - dim_offset - dim_w / 2, cy - 100, "DIM_DATE"),
        (cx + dim_offset - dim_w / 2, cy - 100, "DIM_CUSTOMER"),
        (cx - dim_offset - dim_w / 2, cy + 100 - dim_h, "DIM_PRODUCT"),
        (cx + dim_offset - dim_w / 2, cy + 100 - dim_h, "DIM_GEO"),
    ]
    for dx, dy, label in dim_positions:
        _box(dwg, dx, dy, dim_w, dim_h, fill=WHITE, stroke=ACCENT, stroke_width=1.5)
        _text(
            dwg,
            label,
            dx + dim_w / 2,
            dy + 36,
            font_size=14,
            fill=ACCENT,
            anchor="middle",
            weight="bold",
        )
        line_x1 = dx + dim_w / 2
        line_y1 = dy + dim_h / 2
        if dy < cy:
            line_y2 = cy - fact_h / 2
        else:
            line_y2 = cy + fact_h / 2
        if dx + dim_w < cx:
            line_x2 = cx - fact_w / 2
        else:
            line_x2 = cx + fact_w / 2
        dwg.add(
            dwg.line(
                start=(line_x1, line_y1),
                end=(line_x2, line_y2),
                stroke=ACCENT,
                stroke_width=1.5,
                opacity=0.6,
            )
        )

    _text(
        dwg,
        "Star schema \u00b7 ACID \u00b7 governed",
        wh_x + wh_w / 2,
        wh_y + wh_h - 30,
        font_size=14,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
    )

    # Consumers
    cons_x = 1410
    cons_y = 280
    _draw_consumer_column(dwg, cons_x, cons_y, consumers)

    # Arrows: sources -> ETL
    for i in range(len(sources)):
        ay = src_y + i * 60 + 24
        _arrow(
            dwg,
            src_x + 160,
            ay,
            etl_x,
            ay + (etl_y + 100 + i * 60 + 24 - ay) * 0.5,
            color=ACCENT,
            width=2,
            marker_id=f"a-w-s{i}",
        )
    # ETL -> warehouse
    _arrow(
        dwg,
        etl_x + etl_w,
        etl_y + etl_h / 2,
        wh_x,
        wh_y + wh_h / 2,
        color=ACCENT,
        width=3,
        marker_id="a-w-etl",
    )
    # Warehouse -> consumers
    for i in range(len(consumers)):
        ay = cons_y + i * 60 + 24
        _arrow(
            dwg,
            wh_x + wh_w,
            wh_y + wh_h / 2,
            cons_x,
            ay,
            color=ACCENT,
            width=2,
            marker_id=f"a-w-c{i}",
        )

    # Traits
    _draw_traits(
        dwg,
        100,
        760,
        good_traits=["ACID transactions", "Strong governance", "Sub-second BI"],
        bad_traits=["Structured only", "Schema rigidity", "Expensive at scale", "No ML or gen AI"],
    )

    _draw_tagline(dwg, '"Curate first, then query. The 1990s pattern that still runs the bank."')
    _save(dwg)


# ===========================================================================
# Pattern 2: Data Lake
# ===========================================================================
def gen_lake() -> None:
    dwg = _new_drawing("pattern-lake.svg")
    _draw_background(dwg)
    _draw_title(dwg, "DATA LAKE", "Schema-on-read. Land everything raw. Two stacks emerge.")

    sources = ["Core Banking", "PDFs", "Sensors / IoT", "Streams", "Files"]
    consumers_ds = ["Spark ML", "watsonx.ai", "Studio"]
    consumers_bi = ["Cognos BI", "Reports"]

    src_x, src_y = 80, 220
    _draw_source_column(dwg, src_x, src_y, sources)

    # Ingest stage
    ing_x, ing_y, ing_w, ing_h = 300, 300, 180, 220
    _box(dwg, ing_x, ing_y, ing_w, ing_h, fill=ACCENT_LIGHT, stroke=RULE)
    _text(
        dwg,
        "Ingest",
        ing_x + ing_w / 2,
        ing_y + 32,
        font_size=18,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    ingest_items = ["DataStage", "Kafka", "Spark stream"]
    for i, item in enumerate(ingest_items):
        _box(dwg, ing_x + 16, ing_y + 56 + i * 50, ing_w - 32, 40, fill=WHITE)
        _text(dwg, item, ing_x + ing_w / 2, ing_y + 82 + i * 50, font_size=13, fill=INK2, anchor="middle")

    # Lake storage
    lake_x, lake_y, lake_w, lake_h = 540, 200, 420, 300
    _box(dwg, lake_x, lake_y, lake_w, lake_h, fill=ACCENT_LIGHT, stroke=ACCENT, stroke_width=2)
    _text(
        dwg,
        "Object Storage",
        lake_x + lake_w / 2,
        lake_y + 40,
        font_size=22,
        font_family=FONT_SANS,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
    )
    _text(
        dwg,
        "Bronze / Silver / Gold zones",
        lake_x + lake_w / 2,
        lake_y + 70,
        font_size=14,
        fill=INK2,
        anchor="middle",
        font_family=FONT_SANS,
    )
    formats = [
        ("Parquet", 0, 0),
        ("JSON", 1, 0),
        ("CSV", 2, 0),
        ("Raw files", 0, 1),
        ("Images", 1, 1),
        ("Logs", 2, 1),
    ]
    fmt_w = 110
    fmt_h = 60
    fmt_gap = 12
    grid_x = lake_x + (lake_w - 3 * fmt_w - 2 * fmt_gap) / 2
    grid_y = lake_y + 100
    for fmt, col, row in formats:
        fx = grid_x + col * (fmt_w + fmt_gap)
        fy = grid_y + row * (fmt_h + fmt_gap)
        _box(dwg, fx, fy, fmt_w, fmt_h, fill=WHITE)
        _text(dwg, fmt, fx + fmt_w / 2, fy + fmt_h / 2 + 6, font_size=14, fill=INK2, anchor="middle")
    _text(
        dwg,
        "Schema on read \u00b7 any format",
        lake_x + lake_w / 2,
        lake_y + lake_h - 24,
        font_size=13,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
    )

    # Warehouse side (parallel stack)
    wh_x, wh_y, wh_w, wh_h = 990, 200, 360, 300
    _box(dwg, wh_x, wh_y, wh_w, wh_h, fill=DIM_FILL, stroke=RULE)
    _text(
        dwg,
        "Db2 Warehouse",
        wh_x + wh_w / 2,
        wh_y + 40,
        font_size=20,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    _text(
        dwg,
        "Parallel BI stack",
        wh_x + wh_w / 2,
        wh_y + 70,
        font_size=14,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
    )
    _box(dwg, wh_x + 60, wh_y + 110, wh_w - 120, 140, fill=WHITE)
    _text(
        dwg,
        "Star schemas",
        wh_x + wh_w / 2,
        wh_y + 160,
        font_size=16,
        fill=INK2,
        anchor="middle",
        weight="bold",
    )
    _text(dwg, "for Cognos", wh_x + wh_w / 2, wh_y + 195, font_size=14, fill=SLATE, anchor="middle")
    _text(
        dwg,
        "(duplicate of lake data)",
        wh_x + wh_w / 2,
        wh_y + wh_h - 24,
        font_size=12,
        fill=BAD,
        anchor="middle",
        font_family=FONT_SANS,
        weight="bold",
    )

    # Two-stack callout
    _text(
        dwg,
        "two-stack reality",
        (lake_x + wh_x + wh_w) / 2,
        lake_y - 18,
        font_size=14,
        fill=BAD,
        anchor="middle",
        font_family=FONT_SANS,
        weight="bold",
    )

    # Consumers
    cons_y = 620
    label_y = cons_y - 30
    _text(
        dwg,
        "Data science + ML",
        lake_x + lake_w / 2,
        label_y,
        font_size=14,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
        weight="bold",
    )
    for i, cons in enumerate(consumers_ds):
        cx = lake_x + 30 + i * 130
        _box(dwg, cx, cons_y, 110, 48, fill=ACCENT_LIGHT)
        _text(dwg, cons, cx + 55, cons_y + 30, font_size=13, fill=INK2, anchor="middle")

    _text(
        dwg,
        "BI",
        wh_x + wh_w / 2,
        label_y,
        font_size=14,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
        weight="bold",
    )
    for i, cons in enumerate(consumers_bi):
        cx = wh_x + 60 + i * 130
        _box(dwg, cx, cons_y, 110, 48, fill=ACCENT_LIGHT)
        _text(dwg, cons, cx + 55, cons_y + 30, font_size=13, fill=INK2, anchor="middle")

    # Governance — bolted-on band
    gov_x, gov_y, gov_w, gov_h = 540, 730, 810, 60
    _box(dwg, gov_x, gov_y, gov_w, gov_h, fill=DIM_FILL, stroke=RULE)
    _text(
        dwg,
        "Governance: Knowledge Catalog (added on top, often after the swamp formed)",
        gov_x + gov_w / 2,
        gov_y + 36,
        font_size=14,
        fill=BAD,
        anchor="middle",
        font_family=FONT_SANS,
        weight="bold",
    )

    # Arrows
    for i in range(len(sources)):
        ay = src_y + i * 60 + 24
        _arrow(
            dwg,
            src_x + 160,
            ay,
            ing_x,
            ing_y + ing_h / 2,
            color=ACCENT,
            width=1.5,
            marker_id=f"a-l-s{i}",
        )
    _arrow(
        dwg,
        ing_x + ing_w,
        ing_y + ing_h / 2,
        lake_x,
        lake_y + lake_h / 2,
        color=ACCENT,
        width=2.5,
        marker_id="a-l-lake",
    )
    _arrow(
        dwg,
        ing_x + ing_w,
        ing_y + ing_h / 2,
        wh_x,
        wh_y + wh_h / 2,
        color=ACCENT,
        width=2.5,
        marker_id="a-l-wh",
    )
    _arrow(
        dwg,
        lake_x + lake_w / 2,
        lake_y + lake_h,
        lake_x + lake_w / 2,
        label_y - 14,
        color=ACCENT,
        width=2,
        marker_id="a-l-c1",
    )
    _arrow(
        dwg,
        wh_x + wh_w / 2,
        wh_y + wh_h,
        wh_x + wh_w / 2,
        label_y - 14,
        color=ACCENT,
        width=2,
        marker_id="a-l-c2",
    )

    # Traits
    _draw_traits(
        dwg,
        100,
        830,
        good_traits=["Cheap storage", "Any format", "ML-friendly"],
        bad_traits=["No ACID", "Two stacks \u00b7 duplication", "Governance retroactive", "Becomes a swamp"],
    )

    _draw_tagline(
        dwg,
        '"Schema on read \u2014 when (and if) someone reads it. Two stacks, one source of truth problem."',
    )
    _save(dwg)


# ===========================================================================
# Pattern 3: Data Lakehouse
# ===========================================================================
def gen_lakehouse() -> None:
    dwg = _new_drawing("pattern-lakehouse.svg")
    _draw_background(dwg)
    _draw_title(dwg, "DATA LAKEHOUSE", "Lake economics, warehouse semantics. One copy of data, all workloads.")

    sources = ["Core Banking", "PDFs", "Sensors / IoT", "Streams", "Files"]
    consumers = ["SQL \u00b7 BI", "Spark ML", "watsonx.ai", "Vector / RAG"]

    src_x, src_y = 80, 220
    _draw_source_column(dwg, src_x, src_y, sources)

    # Ingest
    ing_x, ing_y, ing_w, ing_h = 300, 300, 180, 220
    _box(dwg, ing_x, ing_y, ing_w, ing_h, fill=ACCENT_LIGHT, stroke=RULE)
    _text(
        dwg,
        "Ingest",
        ing_x + ing_w / 2,
        ing_y + 32,
        font_size=18,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    ingest_items = ["DataStage", "Kafka", "Replication"]
    for i, item in enumerate(ingest_items):
        _box(dwg, ing_x + 16, ing_y + 56 + i * 50, ing_w - 32, 40, fill=WHITE)
        _text(dwg, item, ing_x + ing_w / 2, ing_y + 82 + i * 50, font_size=13, fill=INK2, anchor="middle")

    # watsonx.data container
    wd_x, wd_y, wd_w, wd_h = 540, 180, 820, 480
    _box(dwg, wd_x, wd_y, wd_w, wd_h, fill=ACCENT_LIGHT, stroke=ACCENT, stroke_width=2)
    _text(
        dwg,
        "watsonx.data",
        wd_x + wd_w / 2,
        wd_y + 36,
        font_size=24,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    _text(
        dwg,
        "Open lakehouse on object storage",
        wd_x + wd_w / 2,
        wd_y + 64,
        font_size=14,
        fill=INK2,
        anchor="middle",
        font_family=FONT_SANS,
    )

    # Layer 3: Iceberg / Delta (highlighted)
    ice_x, ice_y, ice_w, ice_h = wd_x + 60, wd_y + 100, wd_w - 120, 140
    _box(dwg, ice_x, ice_y, ice_w, ice_h, fill=ACCENT, stroke=ACCENT, stroke_width=2)
    _text(
        dwg,
        "APACHE ICEBERG \u00b7 DELTA LAKE \u00b7 MILVUS",
        ice_x + ice_w / 2,
        ice_y + 36,
        font_size=20,
        font_family=FONT_SANS,
        fill=WHITE,
        anchor="middle",
        weight="bold",
    )
    iceberg_features = ["ACID transactions", "Schema evolution", "Time travel", "Vector search"]
    for i, feat in enumerate(iceberg_features):
        col = i % 2
        row = i // 2
        fx = ice_x + 60 + col * (ice_w / 2 - 30)
        fy = ice_y + 70 + row * 32
        _text(dwg, "\u2713 " + feat, fx, fy, font_size=15, fill=ACCENT_LIGHT, weight="bold")

    # Layer 2: Parquet files
    pq_x, pq_y, pq_w, pq_h = wd_x + 60, wd_y + 260, wd_w - 120, 60
    _box(dwg, pq_x, pq_y, pq_w, pq_h, fill=WHITE)
    _text(
        dwg,
        "Parquet files",
        pq_x + pq_w / 2,
        pq_y + 38,
        font_size=15,
        fill=INK2,
        anchor="middle",
        weight="bold",
        font_family=FONT_SANS,
    )

    # Layer 1: Object storage
    os_x, os_y, os_w, os_h = wd_x + 60, wd_y + 330, wd_w - 120, 50
    _box(dwg, os_x, os_y, os_w, os_h, fill=DIM_FILL, stroke=RULE)
    _text(
        dwg,
        "Object storage (S3, COS)",
        os_x + os_w / 2,
        os_y + 32,
        font_size=14,
        fill=SLATE,
        anchor="middle",
        font_family=FONT_SANS,
    )

    # Catalog + governance
    cat_x, cat_y, cat_w, cat_h = wd_x + 60, wd_y + 400, (wd_w - 140) / 2, 60
    _box(dwg, cat_x, cat_y, cat_w, cat_h, fill=ACCENT_LIGHT, stroke=ACCENT)
    _text(
        dwg,
        "Knowledge Catalog",
        cat_x + cat_w / 2,
        cat_y + 26,
        font_size=14,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
        font_family=FONT_SANS,
    )
    _text(
        dwg,
        "Iceberg catalog + lineage",
        cat_x + cat_w / 2,
        cat_y + 46,
        font_size=12,
        fill=INK2,
        anchor="middle",
    )

    gov_x = cat_x + cat_w + 20
    _box(dwg, gov_x, cat_y, cat_w, cat_h, fill=ACCENT_LIGHT, stroke=ACCENT)
    _text(
        dwg,
        "watsonx.governance",
        gov_x + cat_w / 2,
        cat_y + 26,
        font_size=14,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
        font_family=FONT_SANS,
    )
    _text(
        dwg,
        "Built-in policy + factsheets",
        gov_x + cat_w / 2,
        cat_y + 46,
        font_size=12,
        fill=INK2,
        anchor="middle",
    )

    # Consumers
    cons_x, cons_y = 1410, 200
    _text(
        dwg,
        "All workloads, one copy",
        cons_x + 110,
        cons_y - 16,
        font_size=16,
        font_family=FONT_SANS,
        fill=INK,
        anchor="middle",
        weight="bold",
    )
    for i, cons in enumerate(consumers):
        by = cons_y + i * 80
        _box(dwg, cons_x, by, 220, 64, fill=ACCENT_LIGHT)
        _text(
            dwg,
            cons,
            cons_x + 110,
            by + 38,
            font_size=16,
            fill=INK2,
            anchor="middle",
            weight="bold",
            font_family=FONT_SANS,
        )

    # Arrows
    for i in range(len(sources)):
        ay = src_y + i * 60 + 24
        _arrow(
            dwg,
            src_x + 160,
            ay,
            ing_x,
            ing_y + ing_h / 2,
            color=ACCENT,
            width=1.5,
            marker_id=f"a-lh-s{i}",
        )
    _arrow(
        dwg,
        ing_x + ing_w,
        ing_y + ing_h / 2,
        wd_x,
        wd_y + wd_h / 2,
        color=ACCENT,
        width=3,
        marker_id="a-lh-wd",
    )
    for i in range(len(consumers)):
        ay = cons_y + i * 80 + 32
        _arrow(
            dwg,
            wd_x + wd_w,
            wd_y + wd_h / 2,
            cons_x,
            ay,
            color=ACCENT,
            width=2,
            marker_id=f"a-lh-c{i}",
        )

    # Traits
    _draw_traits(
        dwg,
        100,
        760,
        good_traits=[
            "ACID on object storage",
            "Open formats",
            "All workloads \u00b7 one copy",
            "Built-in governance",
            "Vector + ML + BI",
            "watsonx.ai-native",
        ],
    )

    _draw_tagline(dwg, '"Warehouse semantics on lake economics. Where IBM is investing."')
    _save(dwg)


# ===========================================================================
# Pattern 4: Data Fabric
# ===========================================================================
def gen_fabric() -> None:
    dwg = _new_drawing("pattern-fabric.svg")
    _draw_background(dwg)
    _draw_title(
        dwg,
        "DATA FABRIC",
        "Don't move data. Virtualize and govern in place. Active metadata everywhere.",
    )

    # Top band: Active metadata + AI automation
    fab_x, fab_y, fab_w, fab_h = 80, 140, W - 160, 200
    _box(dwg, fab_x, fab_y, fab_w, fab_h, fill=ACCENT, stroke=ACCENT, stroke_width=2, rx=8)
    _text(
        dwg,
        "ACTIVE METADATA + AI AUTOMATION",
        fab_x + fab_w / 2,
        fab_y + 44,
        font_size=24,
        font_family=FONT_SANS,
        fill=WHITE,
        anchor="middle",
        weight="bold",
    )
    _text(
        dwg,
        "Knowledge Catalog \u00b7 watsonx.governance",
        fab_x + fab_w / 2,
        fab_y + 76,
        font_size=15,
        fill=ACCENT_LIGHT,
        anchor="middle",
        font_family=FONT_SANS,
    )
    fab_items = ["Auto discovery", "Auto classify", "Lineage", "Policy engine", "Self-serve"]
    item_w = 240
    item_h = 60
    item_gap = (fab_w - 80 - len(fab_items) * item_w) / (len(fab_items) - 1)
    for i, item in enumerate(fab_items):
        ix = fab_x + 40 + i * (item_w + item_gap)
        _box(dwg, ix, fab_y + 110, item_w, item_h, fill=ACCENT_DEEP, rx=4)
        _text(
            dwg,
            item,
            ix + item_w / 2,
            fab_y + 148,
            font_size=15,
            fill=WHITE,
            anchor="middle",
            weight="bold",
            font_family=FONT_SANS,
        )

    # Distributed data estate
    estate_y = fab_y + fab_h + 80
    _text(
        dwg,
        "Distributed data estate \u00b7 data stays in place",
        fab_x + 20,
        fab_y + fab_h + 50,
        font_size=15,
        font_family=FONT_SANS,
        fill=SLATE,
        anchor="start",
        weight="bold",
    )

    stores = [
        ("Db2 Warehouse", "tables \u00b7 views", 180, ACCENT_LIGHT),
        ("watsonx.data", "Iceberg \u00b7 Delta", 540, ACCENT_LIGHT),
        ("Object storage", "S3 \u00b7 COS \u00b7 Azure", 900, ACCENT_LIGHT),
        ("Mainframe", "Db2 z/OS \u00b7 IMS", 1260, DIM_FILL),
        ("External clouds", "Oracle \u00b7 Snowflake", 1620, DIM_FILL),
    ]
    store_w = 280
    store_h = 200
    for label, sub, cx, fill in stores:
        sx = cx - store_w / 2
        _box(dwg, sx, estate_y, store_w, store_h, fill=fill, stroke=RULE)
        _text(
            dwg,
            label,
            cx,
            estate_y + 36,
            font_size=18,
            font_family=FONT_SANS,
            fill=INK,
            anchor="middle",
            weight="bold",
        )
        _text(dwg, sub, cx, estate_y + 60, font_size=13, fill=SLATE, anchor="middle", font_family=FONT_SANS)
        for j in range(3):
            _box(dwg, sx + 28, estate_y + 90 + j * 32, store_w - 56, 24, fill=WHITE, rx=2)
        _arrow(dwg, cx, fab_y + fab_h, cx, estate_y, color=ACCENT, width=2, marker_id=f"a-f-s{cx}")

    # Consumers band
    cons_y = estate_y + store_h + 50
    cons_h = 80
    _box(dwg, fab_x, cons_y, fab_w, cons_h, fill=ACCENT_LIGHT, rx=8)
    _text(
        dwg,
        "Federated consumers (one query, many sources)",
        fab_x + 30,
        cons_y + 30,
        font_size=16,
        font_family=FONT_SANS,
        fill=INK,
        weight="bold",
    )
    consumers = [
        "Analysts (self-serve)",
        "watsonx.ai \u00b7 agents",
        "Compliance \u00b7 audit",
        "Business apps",
    ]
    for i, cons in enumerate(consumers):
        cx = fab_x + 40 + (i + 0.5) * (fab_w - 80) / len(consumers)
        _text(dwg, cons, cx, cons_y + 60, font_size=14, fill=INK2, anchor="middle", font_family=FONT_SANS)

    # Traits
    _draw_traits(
        dwg,
        100,
        cons_y + cons_h + 40,
        good_traits=[
            "Spans heterogeneous estates",
            "AI-driven governance",
            "No data movement",
            "Sovereignty preserved",
        ],
    )

    _draw_tagline(dwg, '"The metadata layer that knows where everything is. Architectural style, not a place."')
    _save(dwg)


# ===========================================================================
# Pattern 5: Data Mesh
# ===========================================================================
def gen_mesh() -> None:
    dwg = _new_drawing("pattern-mesh.svg")
    _draw_background(dwg)
    _draw_title(dwg, "DATA MESH", "Domains own their data products. Federated computational governance.")

    # Four domains
    domains = [
        ("Retail Banking", ["Customer 360", "Transactions"], ["Lakehouse + catalog", "Owns customer 360"]),
        ("Capital Markets", ["Trade book", "Positions"], ["Lakehouse + catalog", "Owns trade book"]),
        (
            "Wealth \u00b7 Insurance",
            ["Policy 360", "Claims"],
            ["Lakehouse + catalog", "Owns policy 360"],
        ),
        (
            "Risk \u00b7 Compliance",
            ["Regulatory views", "AML"],
            ["Lakehouse + catalog", "Cross-domain views"],
        ),
    ]

    domain_y = 140
    domain_w = 420
    domain_h = 360
    gap = 40
    total_w = len(domains) * domain_w + (len(domains) - 1) * gap
    start_x = (W - total_w) / 2

    for i, (name, products, descs) in enumerate(domains):
        dx = start_x + i * (domain_w + gap)

        _box(dwg, dx, domain_y, domain_w, domain_h, fill=WHITE, stroke=ACCENT, stroke_width=2, rx=10)
        _text(
            dwg,
            name,
            dx + domain_w / 2,
            domain_y + 38,
            font_size=20,
            font_family=FONT_SANS,
            fill=ACCENT,
            anchor="middle",
            weight="bold",
        )
        _text(
            dwg,
            "Domain team owns end-to-end",
            dx + domain_w / 2,
            domain_y + 64,
            font_size=12,
            fill=SLATE,
            anchor="middle",
            font_family=FONT_SANS,
        )

        # Lakehouse infra
        lh_x, lh_y = dx + 30, domain_y + 90
        lh_w, lh_h = domain_w - 60, 80
        _box(dwg, lh_x, lh_y, lh_w, lh_h, fill=ACCENT_LIGHT)
        _text(
            dwg,
            descs[0],
            lh_x + lh_w / 2,
            lh_y + 32,
            font_size=14,
            fill=INK,
            anchor="middle",
            weight="bold",
        )
        _text(
            dwg,
            "Iceberg tables \u00b7 local catalog",
            lh_x + lh_w / 2,
            lh_y + 56,
            font_size=11,
            fill=SLATE,
            anchor="middle",
            font_family=FONT_SANS,
        )

        # Data products
        dp_x, dp_y = dx + 30, domain_y + 190
        dp_w, dp_h = domain_w - 60, 130
        _box(dwg, dp_x, dp_y, dp_w, dp_h, fill=ACCENT_LIGHT, stroke=ACCENT, stroke_width=2)
        _text(
            dwg,
            "DATA PRODUCTS",
            dp_x + dp_w / 2,
            dp_y + 26,
            font_size=14,
            fill=ACCENT,
            anchor="middle",
            weight="bold",
            font_family=FONT_SANS,
        )
        for j, prod in enumerate(products):
            py = dp_y + 46 + j * 32
            _box(dwg, dp_x + 16, py, dp_w - 32, 26, fill=WHITE, stroke=ACCENT)
            _text(
                dwg,
                prod,
                dp_x + dp_w / 2,
                py + 18,
                font_size=13,
                fill=ACCENT,
                anchor="middle",
                weight="bold",
            )
        _text(
            dwg,
            "SLA \u00b7 contract \u00b7 schema \u00b7 owner",
            dp_x + dp_w / 2,
            dp_y + dp_h - 14,
            font_size=11,
            fill=SLATE,
            anchor="middle",
            font_family=FONT_SANS,
        )

    # Contract arrows
    for i in range(len(domains) - 1):
        x1 = start_x + i * (domain_w + gap) + domain_w
        x2 = start_x + (i + 1) * (domain_w + gap)
        ay = domain_y + domain_h / 2
        _arrow(dwg, x1, ay - 12, x2, ay - 12, color=ACCENT, width=2, marker_id=f"a-m-c{i}a")
        _arrow(dwg, x2, ay + 12, x1, ay + 12, color=ACCENT, width=2, marker_id=f"a-m-c{i}b")
        _text(
            dwg,
            "contracts",
            (x1 + x2) / 2,
            ay - 22,
            font_size=12,
            fill=ACCENT,
            anchor="middle",
            font_family=FONT_SANS,
            weight="bold",
        )

    # Platform team band
    plat_y = domain_y + domain_h + 60
    plat_h = 110
    _box(dwg, start_x - 20, plat_y, total_w + 40, plat_h, fill=ACCENT, rx=10)
    _text(
        dwg,
        "Platform Team \u00b7 Cloud Pak for Data",
        (start_x + total_w / 2),
        plat_y + 38,
        font_size=22,
        font_family=FONT_SANS,
        fill=WHITE,
        anchor="middle",
        weight="bold",
    )
    plat_items = [
        "Federated catalog",
        "Governance policies",
        "Self-serve infra",
        "Observability",
        "Standards \u00b7 contracts",
    ]
    for i, item in enumerate(plat_items):
        ix = start_x + 60 + i * (total_w - 120) / (len(plat_items) - 1)
        _text(dwg, item, ix, plat_y + 78, font_size=14, fill=ACCENT_LIGHT, anchor="middle", font_family=FONT_SANS)

    # Arrows to platform
    for i in range(len(domains)):
        dx = start_x + i * (domain_w + gap) + domain_w / 2
        _arrow(dwg, dx, domain_y + domain_h, dx, plat_y, color=RULE, width=1.5, marker_id=f"a-m-p{i}")

    # Key principle callout
    cp_y = plat_y + plat_h + 30
    _box(dwg, start_x, cp_y, total_w, 56, fill=ACCENT_LIGHT, rx=6, stroke=ACCENT)
    _text(
        dwg,
        "Key principle: domain teams own their data as a product. Platform enables \u2014 does not centralize.",
        start_x + total_w / 2,
        cp_y + 36,
        font_size=15,
        fill=ACCENT,
        anchor="middle",
        weight="bold",
        font_family=FONT_SANS,
    )

    # Traits
    _draw_traits(
        dwg,
        100,
        cp_y + 90,
        good_traits=[
            "Domain ownership",
            "Federated governance",
            "Scales with org",
            "Data products with SLAs",
        ],
    )

    _draw_tagline(dwg, '"An org change, expressed in YAML. Mesh is who owns it, not where it lives."')
    _save(dwg)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    _ensure_output()
    print("Generating pattern diagrams...")
    gen_warehouse()
    gen_lake()
    gen_lakehouse()
    gen_fabric()
    gen_mesh()
    print(f"\nDone. Files in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
