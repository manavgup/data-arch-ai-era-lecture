#!/usr/bin/env python3
"""Generate SVG pattern architecture diagrams in the style of the reference SVG.

Each pattern gets a single-column vertical flow diagram with arrows.
Plus one comparison SVG with all 5 side by side.

Output: deck/assets/pattern-{name}.svg (and .png via cairosvg if available)
"""

from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

# ── Style tokens ──────────────────────────────────────────────────────────────

FONT = '"Inter", "Helvetica Neue", Helvetica, Arial, sans-serif'
MONO = '"JetBrains Mono", "Consolas", ui-monospace, monospace'

# Outer column background per pattern (dark, distinctive)
PALETTES = {
    "warehouse": {"bg": "rgb(12,68,124)", "stroke": "rgb(133,183,235)", "title": "rgb(250,249,245)", "subtitle": "rgb(194,192,182)"},
    "lake": {"bg": "rgb(8,80,65)", "stroke": "rgb(93,202,165)", "title": "rgb(250,249,245)", "subtitle": "rgb(194,192,182)"},
    "lakehouse": {"bg": "rgb(60,52,137)", "stroke": "rgb(175,169,236)", "title": "rgb(250,249,245)", "subtitle": "rgb(194,192,182)"},
    "mesh": {"bg": "rgb(45,74,222)", "stroke": "rgb(140,160,240)", "title": "rgb(250,249,245)", "subtitle": "rgb(194,192,182)"},
    "fabric": {"bg": "rgb(120,60,0)", "stroke": "rgb(220,170,100)", "title": "rgb(250,249,245)", "subtitle": "rgb(194,192,182)"},
}

# Consistent colors across ALL diagrams
LAYER_BOX_FILL = "rgb(255,255,255)"        # White layer boxes (Consumption, Storage, etc.)
LAYER_BOX_STROKE = "rgb(200,200,200)"      # Light gray border
LAYER_LABEL_COLOR = "rgb(21,23,26)"        # Dark ink for layer labels
CHIP_FILL = "rgb(208,226,255)"             # IBM light blue — consistent across all diagrams
CHIP_STROKE = "rgb(141,180,240)"           # Slightly darker blue border
CHIP_TEXT = "rgb(0,43,128)"                # Deep blue text on chips

ARROW_COLOR = "rgb(156,154,146)"


# ── Pattern definitions ───────────────────────────────────────────────────────

PATTERNS = {
    "warehouse": {
        "title": "Data Warehouse",
        "subtitle": "Structured, schema on write",
        "layers": [
            ("Consumption", ["Cognos BI", "Reports", "Planning Analytics"]),
            ("Storage", ["Db2 Warehouse", "Db2 for z/OS, Netezza", "Conformed star schemas"]),
            ("ETL", ["DataStage", "Data Replication"]),
            ("Governance", ["Knowledge Catalog", "Data Quality", "MDM Match 360"]),
            ("Sources", ["Core banking, ERP", "Mainframe, Db2 z/OS", "Structured only"]),
        ],
    },
    "lake": {
        "title": "Data Lake",
        "subtitle": "Raw, schema on read",
        "layers": [
            ("Consumption", ["Cognos BI", "watsonx.ai", "Watson Studio", "SPSS, Spark ML"]),
            ("Curated zone", ["Db2 Warehouse", "For BI workloads"]),
            ("Raw zone (lake)", ["Object storage (S3, COS)", "Parquet, JSON, files"]),
            ("ETL and processing", ["DataStage", "Spark, Hadoop"]),
            ("Governance (added on)", ["Knowledge Catalog"]),
            ("Sources", ["Structured, semi, unstructured"]),
        ],
    },
    "lakehouse": {
        "title": "Data Lakehouse",
        "subtitle": "One copy, all workloads",
        "layers": [
            ("Consumption", ["Cognos BI", "watsonx.ai", "Watson Studio", "Agents, RAG"]),
            ("Query engines", ["Presto, Spark", "Db2 engine"]),
            ("Open table formats", ["Apache Iceberg", "Delta Lake, Milvus vector"]),
            ("Object storage", ["S3 / COS / MinIO", "Parquet underneath"]),
            ("ETL + streaming", ["DataStage, CDC", "Kafka, real-time"]),
            ("Sources", ["Structured + unstructured + streaming"]),
        ],
    },
    "mesh": {
        "title": "Data Mesh",
        "subtitle": "Domain-owned data products",
        "layers": [
            ("Cross-domain consumers", ["Customer 360", "Fraud modelling", "Reg reporting"]),
            ("Data product contracts", ["Schema contracts", "SLAs, freshness"]),
            ("Domain lakehouses", ["Cards (Iceberg)", "Retail (Iceberg)", "Wealth (Iceberg)"]),
            ("Per-domain pipelines", ["Domain-owned ETL", "Schema registry"]),
            ("Platform team", ["Catalog, discovery", "Federated governance"]),
            ("Domain sources", ["Cards systems", "Retail systems", "Wealth systems"]),
        ],
    },
    "fabric": {
        "title": "Data Fabric",
        "subtitle": "AI-driven governance layer",
        "layers": [
            ("Self-serve discovery", ["Knowledge Catalog", "Auto recommendations"]),
            ("AI metadata layer", ["AI classification", "Automated lineage", "Quality monitoring"]),
            ("Underlying patterns", ["Warehouse", "Lakehouse", "Lake", "External"]),
            ("Policy-aware routing", ["Schema drift detection", "Governance-first ingestion"]),
            ("Heterogeneous sources", ["Db2, Oracle, Iceberg", "PDFs, APIs, third-party"]),
        ],
    },
}


def _svg_column(x_off, col_w, col_h, pattern_key, layers, title, subtitle, palette):
    """Generate SVG elements for one pattern column."""
    bg = palette["bg"]
    stroke = palette["stroke"]
    title_col = palette["title"]
    subtitle_col = palette["subtitle"]

    parts = []
    rx = 12
    pad = 15
    inner_w = col_w - 2 * pad
    layer_gap = 25

    # Outer column background (dark, pattern-specific)
    parts.append(f'  <rect x="{x_off}" y="20" width="{col_w}" height="{col_h}" rx="{rx}" fill="{bg}" stroke="{stroke}" stroke-width="0.5"/>')
    # Title
    cx = x_off + col_w / 2
    parts.append(f'  <text x="{cx}" y="50" text-anchor="middle" font-family=\'{FONT}\' font-size="16" font-weight="500" fill="{title_col}">{title}</text>')
    parts.append(f'  <text x="{cx}" y="68" text-anchor="middle" font-family=\'{FONT}\' font-size="12" fill="{subtitle_col}">{subtitle}</text>')

    # Calculate layer heights
    n = len(layers)
    total_arrows = (n - 1) * layer_gap
    available = col_h - 80 - 20 - total_arrows  # header space + bottom pad
    layer_h_base = available / n

    y = 90
    for li, (layer_name, items) in enumerate(layers):
        # Size layer by item count
        item_h = max(len(items) * 24 + 30, layer_h_base)
        lx = x_off + pad
        lw = inner_w

        # Layer box (white/light)
        parts.append(f'  <rect x="{lx}" y="{y}" width="{lw}" height="{item_h}" rx="8" fill="{LAYER_BOX_FILL}" stroke="{LAYER_BOX_STROKE}" stroke-width="0.5"/>')
        # Layer label (dark text on white)
        parts.append(f'  <text x="{lx + lw/2}" y="{y + 20}" text-anchor="middle" font-family=\'{FONT}\' font-size="14" font-weight="600" fill="{LAYER_LABEL_COLOR}">{layer_name}</text>')

        # Chips (IBM light blue, consistent across all diagrams)
        chip_y = y + 30
        for item in items:
            tw = min(lw - 20, max(len(item) * 7.5 + 16, 80))
            chip_x = lx + (lw - tw) / 2
            parts.append(f'  <rect x="{chip_x}" y="{chip_y}" width="{tw}" height="20" rx="4" fill="{CHIP_FILL}" stroke="{CHIP_STROKE}" stroke-width="0.5"/>')
            parts.append(f'  <text x="{chip_x + tw/2}" y="{chip_y + 14}" text-anchor="middle" font-family=\'{FONT}\' font-size="12" fill="{CHIP_TEXT}">{item}</text>')
            chip_y += 24

        box_bottom = y + item_h

        # Arrow to next layer
        if li < n - 1:
            arrow_x = x_off + col_w / 2
            parts.append(f'  <line x1="{arrow_x}" y1="{box_bottom}" x2="{arrow_x}" y2="{box_bottom + layer_gap}" stroke="{ARROW_COLOR}" stroke-width="1.5" marker-end="url(#arrow)"/>')

        y = box_bottom + layer_gap

    return parts, y


def generate_single_pattern_svg(name, pattern, palette, width=280, filename=None):
    """Generate a single-column SVG for one pattern."""
    layers = pattern["layers"]
    # Estimate height
    total_items = sum(len(items) for _, items in layers)
    est_h = 90 + len(layers) * 50 + total_items * 24 + (len(layers) - 1) * 25 + 30
    col_h = max(est_h, 500)

    parts = [
        f'<svg width="100%" viewBox="0 0 {width} {col_h + 40}" xmlns="http://www.w3.org/2000/svg">',
        f'  <title>{pattern["title"]} architecture pattern</title>',
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
        '    </marker>',
        '  </defs>',
    ]

    col_parts, _ = _svg_column(10, width - 20, col_h, name, layers, pattern["title"], pattern["subtitle"], palette)
    parts.extend(col_parts)
    parts.append('</svg>')

    out = ASSETS / (filename or f"pattern-{name}.svg")
    out.write_text("\n".join(parts))
    print(f"  {out.name}")
    return out


def generate_comparison_svg():
    """Generate a side-by-side comparison SVG with all 5 patterns."""
    col_w = 220
    gap = 12
    n = 5
    total_w = n * col_w + (n - 1) * gap + 20  # 10px padding each side

    # Find max height needed
    max_items = 0
    for p in PATTERNS.values():
        total = sum(len(items) for _, items in p["layers"])
        n_layers = len(p["layers"])
        h = 90 + n_layers * 50 + total * 24 + (n_layers - 1) * 25 + 30
        max_items = max(max_items, h)
    col_h = max(max_items, 600)

    parts = [
        f'<svg width="100%" viewBox="0 0 {total_w} {col_h + 40}" xmlns="http://www.w3.org/2000/svg">',
        '  <title>Five data architecture patterns compared side by side</title>',
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
        '    </marker>',
        '  </defs>',
    ]

    x = 10
    for name in ["warehouse", "lake", "lakehouse", "mesh", "fabric"]:
        pattern = PATTERNS[name]
        palette = PALETTES[name]
        col_parts, _ = _svg_column(x, col_w, col_h, name, pattern["layers"], pattern["title"], pattern["subtitle"], palette)
        parts.extend(col_parts)
        x += col_w + gap

    parts.append('</svg>')

    out = ASSETS / "pattern-comparison.svg"
    out.write_text("\n".join(parts))
    print(f"  {out.name}")
    return out


def convert_to_png(svg_path):
    """Convert SVG to PNG using cairosvg."""
    try:
        import cairosvg
        png_path = svg_path.with_suffix(".png")
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), scale=2)
        print(f"  {png_path.name}")
        return png_path
    except ImportError:
        print("  (cairosvg not installed — skipping PNG conversion)")
        return None


def main():
    print("Generating pattern SVGs...")
    svg_files = []

    for name, pattern in PATTERNS.items():
        svg = generate_single_pattern_svg(name, pattern, PALETTES[name])
        svg_files.append(svg)

    comparison = generate_comparison_svg()
    svg_files.append(comparison)

    print("\nConverting to PNG...")
    for svg in svg_files:
        convert_to_png(svg)

    print("\nDone.")


if __name__ == "__main__":
    main()
