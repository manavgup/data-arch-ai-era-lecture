#!/usr/bin/env python3
"""Generate synthetic BFSI dataset for Data Architecture for the AI Era lecture.

Fictional bank: Maple Trust Bank — a mid-size Canadian bank.
Produces tabular data (Parquet), policy PDFs, eval JSONL, lineage JSON, and MDM links.

Usage:
    python data/generate.py                # default seed=42
    python data/generate.py --seed 123     # custom seed
    python data/generate.py --output-dir /tmp/data  # custom output
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent

REGIONS = ["Ontario", "Quebec", "BC", "Alberta", "Atlantic", "Prairies"]

CANADIAN_CITIES = {
    "Ontario": [
        "Toronto", "Ottawa", "Mississauga", "Hamilton", "London",
        "Brampton", "Markham", "Kitchener", "Windsor", "Burlington",
    ],
    "Quebec": [
        "Montreal", "Quebec City", "Laval", "Gatineau", "Sherbrooke",
        "Longueuil", "Trois-Rivieres", "Saguenay",
    ],
    "BC": [
        "Vancouver", "Victoria", "Surrey", "Burnaby", "Richmond",
        "Kelowna", "Nanaimo", "Kamloops",
    ],
    "Alberta": [
        "Calgary", "Edmonton", "Red Deer", "Lethbridge", "Medicine Hat",
        "Grande Prairie", "Fort McMurray",
    ],
    "Atlantic": [
        "Halifax", "Saint John", "Fredericton", "St. John's",
        "Charlottetown", "Moncton",
    ],
    "Prairies": [
        "Winnipeg", "Regina", "Saskatoon", "Brandon", "Moose Jaw",
    ],
}

BRANCH_NAMES = {
    "Ontario": [
        "Downtown Toronto", "Toronto Financial District", "Mississauga Square",
        "Ottawa Parliament", "Hamilton Centre", "London Main", "Brampton Gateway",
        "Markham Pacific Mall", "Kitchener Uptown", "Windsor Riverside",
        "Burlington Lakeshore", "Scarborough Town Centre", "North York Yonge",
    ],
    "Quebec": [
        "Montreal Place Ville-Marie", "Montreal Saint-Catherine", "Quebec City Old Port",
        "Laval Carrefour", "Gatineau Hull", "Sherbrooke King",
        "Longueuil Metro", "Trois-Rivieres Centre",
    ],
    "BC": [
        "Vancouver Main", "Vancouver Robson", "Victoria Inner Harbour",
        "Surrey Central", "Burnaby Metrotown", "Richmond No. 3 Road",
        "Kelowna Bernard", "Nanaimo Terminal",
    ],
    "Alberta": [
        "Calgary Stephen Avenue", "Calgary Chinook", "Edmonton Jasper Avenue",
        "Edmonton West End", "Red Deer Gaetz", "Lethbridge Centre",
        "Fort McMurray Franklin",
    ],
    "Atlantic": [
        "Halifax Spring Garden", "Halifax Barrington", "Saint John King",
        "Fredericton Queen", "St. John's Water Street", "Moncton Main",
    ],
    "Prairies": [
        "Winnipeg Portage", "Winnipeg St. Vital", "Regina Albert",
        "Saskatoon Broadway", "Brandon Rosser",
    ],
}

PROVINCE_CODES = {
    "Ontario": "ON", "Quebec": "QC", "BC": "BC",
    "Alberta": "AB", "Atlantic": "NS", "Prairies": "MB",
}

POSTAL_PREFIXES = {
    "Ontario": ["M", "K", "L", "N", "P"],
    "Quebec": ["H", "G", "J"],
    "BC": ["V"],
    "Alberta": ["T"],
    "Atlantic": ["B", "E", "A", "C"],
    "Prairies": ["R", "S"],
}

RESIDENCY_CHOICES = ["Canada", "US", "UK", "India", "China", "Other"]
RESIDENCY_WEIGHTS = [0.90, 0.03, 0.02, 0.02, 0.02, 0.01]

KYC_CHOICES = ["verified", "pending", "expired", "flagged"]
KYC_WEIGHTS = [0.80, 0.10, 0.05, 0.05]

SEGMENT_CHOICES = ["retail", "commercial", "wealth", "institutional"]
SEGMENT_WEIGHTS = [0.60, 0.20, 0.15, 0.05]

ACCOUNT_STATUS_CHOICES = ["active", "dormant", "closed"]
ACCOUNT_STATUS_WEIGHTS = [0.85, 0.10, 0.05]

ACCOUNT_TYPES = ["chequing", "savings", "investment", "mortgage", "credit"]

BALANCE_RANGES = {
    "chequing": (100.0, 50_000.0),
    "savings": (500.0, 200_000.0),
    "investment": (5_000.0, 2_000_000.0),
    "mortgage": (-500_000.0, -50_000.0),
    "credit": (-25_000.0, 0.0),
}

TXN_TYPES = ["deposit", "withdrawal", "transfer", "payment", "wire"]
TXN_CHANNELS = ["branch", "online", "mobile", "ATM", "phone"]
TXN_CHANNEL_WEIGHTS = [0.10, 0.30, 0.35, 0.15, 0.10]
CURRENCY_CHOICES = ["CAD", "USD", "EUR", "GBP"]
CURRENCY_WEIGHTS = [0.95, 0.03, 0.01, 0.01]


# ---------------------------------------------------------------------------
# Tabular generators
# ---------------------------------------------------------------------------


def generate_branches(seed: int = 42) -> pd.DataFrame:
    """Generate 50 branch records for Maple Trust Bank."""
    rng = random.Random(seed)

    rows = []
    branch_idx = 0
    # Distribute branches proportionally: ON 13, QC 8, BC 8, AB 7, ATL 6, PR 5 → 47 + 3 extra
    region_alloc = {
        "Ontario": 13, "Quebec": 8, "BC": 8,
        "Alberta": 7, "Atlantic": 6, "Prairies": 5,
    }
    # We have 50 names total across BRANCH_NAMES, which is ≥50 by design
    extra_needed = 50 - sum(region_alloc.values())

    for region, count in region_alloc.items():
        names = BRANCH_NAMES[region][:count]
        cities = CANADIAN_CITIES[region]
        for i, name in enumerate(names):
            branch_idx += 1
            city = cities[i % len(cities)]
            prov = PROVINCE_CODES[region]
            prefix = rng.choice(POSTAL_PREFIXES[region])
            postal = f"{prefix}{rng.randint(1,9)}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')} {rng.randint(1,9)}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{rng.randint(0,9)}"
            street_num = rng.randint(1, 999)
            street = rng.choice([
                "King Street", "Queen Street", "Main Street", "Bay Street",
                "Yonge Street", "Bloor Street", "University Avenue",
                "Maple Drive", "Oak Boulevard", "Cedar Road",
                "First Avenue", "Elm Street", "Pine Crescent",
            ])
            address = f"{street_num} {street}, {city}, {prov} {postal}"
            rows.append({
                "branch_id": f"MTB-{branch_idx:03d}",
                "name": name,
                "address": address,
                "region": region,
                "manager_id": f"MGR-{branch_idx:03d}",
            })

    # fill any extras from Ontario
    while len(rows) < 50:
        branch_idx += 1
        extra_names = ["Oshawa Simcoe", "Barrie Bayfield", "Guelph Gordon"]
        name = extra_names[len(rows) - 47] if (len(rows) - 47) < len(extra_names) else f"Branch {branch_idx}"
        city = rng.choice(CANADIAN_CITIES["Ontario"])
        prov = "ON"
        prefix = rng.choice(POSTAL_PREFIXES["Ontario"])
        postal = f"{prefix}{rng.randint(1,9)}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')} {rng.randint(1,9)}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{rng.randint(0,9)}"
        street_num = rng.randint(1, 999)
        street = rng.choice(["King Street", "Queen Street", "Main Street"])
        address = f"{street_num} {street}, {city}, ON {postal}"
        rows.append({
            "branch_id": f"MTB-{branch_idx:03d}",
            "name": name,
            "address": address,
            "region": "Ontario",
            "manager_id": f"MGR-{branch_idx:03d}",
        })

    df = pd.DataFrame(rows)
    return df


def generate_customers(seed: int = 42, n: int = 100_000) -> pd.DataFrame:
    """Generate 100K customer records."""
    fake = Faker("en_CA")
    Faker.seed(seed)
    rng = np.random.default_rng(seed)

    customer_ids = [f"CUST-{i+1:06d}" for i in range(n)]
    names = [fake.name() for _ in range(n)]
    dobs = [datetime.date.fromordinal(o) for o in rng.integers(
        datetime.date(1940, 1, 1).toordinal(),
        datetime.date(2005, 12, 31).toordinal(),
        size=n,
    )]
    residencies = rng.choice(RESIDENCY_CHOICES, size=n, p=RESIDENCY_WEIGHTS).tolist()
    kyc_statuses = rng.choice(KYC_CHOICES, size=n, p=KYC_WEIGHTS).tolist()
    # risk_score skewed low: use beta distribution
    risk_scores = (rng.beta(2, 8, size=n) * 100).astype(int).clip(1, 100)
    opened_dates = [
        datetime.date.fromordinal(o)
        for o in rng.integers(
            datetime.date(2000, 1, 1).toordinal(),
            datetime.date(2025, 6, 30).toordinal(),
            size=n,
        )
    ]
    segments = rng.choice(SEGMENT_CHOICES, size=n, p=SEGMENT_WEIGHTS).tolist()

    df = pd.DataFrame({
        "customer_id": customer_ids,
        "name": names,
        "dob": dobs,
        "residency": residencies,
        "kyc_status": kyc_statuses,
        "risk_score": risk_scores,
        "opened_date": opened_dates,
        "segment": segments,
    })
    df["dob"] = pd.to_datetime(df["dob"])
    df["opened_date"] = pd.to_datetime(df["opened_date"])
    return df


def generate_accounts(
    customers_df: pd.DataFrame,
    branches_df: pd.DataFrame,
    seed: int = 42,
    n: int = 200_000,
) -> pd.DataFrame:
    """Generate 200K account records linked to customers and branches."""
    rng = np.random.default_rng(seed)
    py_rng = random.Random(seed)

    customer_ids = customers_df["customer_id"].values
    branch_ids = branches_df["branch_id"].values
    cust_opened = dict(
        zip(customers_df["customer_id"], pd.to_datetime(customers_df["opened_date"]))
    )

    # Assign 1-5 accounts per customer using a weighted distribution
    n_customers = len(customer_ids)
    # weights: 1→30%, 2→35%, 3→20%, 4→10%, 5→5%
    accts_per_cust = rng.choice([1, 2, 3, 4, 5], size=n_customers, p=[0.30, 0.35, 0.20, 0.10, 0.05])

    # Build assignment list
    cust_assignments = []
    for cid, num_accts in zip(customer_ids, accts_per_cust):
        cust_assignments.extend([cid] * num_accts)

    # Trim or extend to exactly n
    if len(cust_assignments) > n:
        cust_assignments = cust_assignments[:n]
    else:
        while len(cust_assignments) < n:
            cust_assignments.append(py_rng.choice(customer_ids))

    rng.shuffle(cust_assignments)

    assigned_branches = rng.choice(branch_ids, size=n)
    account_types = rng.choice(ACCOUNT_TYPES, size=n)
    statuses = rng.choice(ACCOUNT_STATUS_CHOICES, size=n, p=ACCOUNT_STATUS_WEIGHTS)

    # Opened dates: >= customer opened_date, up to 2025-06-30
    max_ord = datetime.date(2025, 6, 30).toordinal()
    opened_dates = []
    for cid in cust_assignments:
        cust_date = cust_opened[cid]
        if isinstance(cust_date, pd.Timestamp):
            cust_ord = cust_date.date().toordinal()
        else:
            cust_ord = cust_date.toordinal()
        start = min(cust_ord, max_ord - 1)
        opened_dates.append(datetime.date.fromordinal(rng.integers(start, max_ord)))

    # Balances by account type
    balances = []
    for atype in account_types:
        lo, hi = BALANCE_RANGES[atype]
        balances.append(round(rng.uniform(lo, hi), 2))

    df = pd.DataFrame({
        "account_id": [f"ACCT-{i+1:06d}" for i in range(n)],
        "customer_id": cust_assignments,
        "branch_id": assigned_branches,
        "account_type": account_types,
        "opened_date": opened_dates,
        "status": statuses,
        "balance": balances,
    })
    df["opened_date"] = pd.to_datetime(df["opened_date"])
    return df


def generate_transactions(
    accounts_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    seed: int = 42,
    n: int = 1_000_000,
) -> pd.DataFrame:
    """Generate 1M transaction records with ~50 suspicious AML signals."""
    rng = np.random.default_rng(seed)
    py_rng = random.Random(seed)

    acct_ids = accounts_df["account_id"].values
    acct_branch = dict(zip(accounts_df["account_id"], accounts_df["branch_id"]))
    acct_customer = dict(zip(accounts_df["account_id"], accounts_df["customer_id"]))
    customer_ids_list = customers_df["customer_id"].tolist()

    # Identify high-risk / flagged accounts for AML seeding
    flagged_customers = set(
        customers_df.loc[
            (customers_df["kyc_status"] == "flagged") | (customers_df["risk_score"] >= 80),
            "customer_id",
        ]
    )
    flagged_accounts = accounts_df.loc[
        (accounts_df["customer_id"].isin(flagged_customers)) & (accounts_df["status"] == "active"),
        "account_id",
    ].values
    if len(flagged_accounts) == 0:
        # fallback: just use first 50 active accounts
        flagged_accounts = accounts_df.loc[accounts_df["status"] == "active", "account_id"].values[:50]

    print(f"  Found {len(flagged_accounts)} flagged/high-risk accounts for AML seeding")

    # Pre-generate arrays for performance
    selected_accts = rng.choice(acct_ids, size=n)
    amounts_raw = rng.lognormal(mean=4.0, sigma=1.5, size=n)  # mostly small, some large
    amounts = np.round(amounts_raw.clip(0.50, 15_000.0), 2)
    currencies = rng.choice(CURRENCY_CHOICES, size=n, p=CURRENCY_WEIGHTS)
    txn_types = rng.choice(TXN_TYPES, size=n)
    channels = rng.choice(TXN_CHANNELS, size=n, p=TXN_CHANNEL_WEIGHTS)

    # Timestamps: business-hour weighted over 2023-01-01 to 2024-12-31
    start_ts = datetime.datetime(2023, 1, 1, 0, 0, 0)
    end_ts = datetime.datetime(2024, 12, 31, 23, 59, 59)
    total_seconds = int((end_ts - start_ts).total_seconds())

    # Generate timestamps with business-hour bias
    raw_offsets = rng.integers(0, total_seconds, size=n)
    timestamps = []
    for off in raw_offsets:
        dt = start_ts + datetime.timedelta(seconds=int(off))
        # Bias toward business hours: if outside 8am-6pm, 60% chance to re-roll hour
        if dt.hour < 8 or dt.hour >= 18:
            if rng.random() < 0.6:
                dt = dt.replace(hour=rng.integers(8, 18))
        # Slight bias away from weekends
        if dt.weekday() >= 5:
            if rng.random() < 0.4:
                dt = dt - datetime.timedelta(days=dt.weekday() - 4)
        timestamps.append(dt)

    # Counterparties
    counterparties = []
    for i in range(n):
        if rng.random() < 0.3:
            counterparties.append(f"EXTERNAL-{rng.integers(1000, 9999):04d}")
        else:
            counterparties.append(py_rng.choice(customer_ids_list))

    # Seed ~50 suspicious transactions
    suspicious_indices = rng.choice(n, size=50, replace=False)
    for idx in suspicious_indices:
        selected_accts[idx] = py_rng.choice(flagged_accounts)
        amounts[idx] = round(rng.uniform(50_000, 500_000), 2)
        txn_types[idx] = py_rng.choice(["wire", "transfer", "deposit"])
        channels[idx] = py_rng.choice(["branch", "online"])
        counterparties[idx] = f"EXTERNAL-{rng.integers(1000, 9999):04d}"

    # Build branch_ids from account mapping
    branch_ids = [acct_branch[a] for a in selected_accts]

    df = pd.DataFrame({
        "transaction_id": [f"TXN-{i+1:07d}" for i in range(n)],
        "account_id": selected_accts,
        "branch_id": branch_ids,
        "amount": amounts,
        "currency": currencies,
        "timestamp": timestamps,
        "transaction_type": txn_types,
        "channel": channels,
        "counterparty_id": counterparties,
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ---------------------------------------------------------------------------
# Policy PDF generator
# ---------------------------------------------------------------------------

def generate_policies(output_dir: Path, seed: int = 42) -> None:
    """Generate 10 professional policy PDFs using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        NextPageTemplate,
        PageBreak,
        PageTemplate,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    policies_dir = output_dir / "policies"
    policies_dir.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()

    # Custom styles
    style_title = ParagraphStyle(
        "PolicyTitle", parent=styles["Title"],
        fontSize=22, leading=26, spaceAfter=20, alignment=TA_CENTER,
    )
    style_subtitle = ParagraphStyle(
        "PolicySubtitle", parent=styles["Normal"],
        fontSize=12, leading=14, spaceAfter=30, alignment=TA_CENTER,
        textColor=colors.grey,
    )
    style_h1 = ParagraphStyle(
        "PolicyH1", parent=styles["Heading1"],
        fontSize=16, leading=20, spaceBefore=18, spaceAfter=10,
        textColor=colors.HexColor("#003366"),
    )
    style_h2 = ParagraphStyle(
        "PolicyH2", parent=styles["Heading2"],
        fontSize=13, leading=16, spaceBefore=12, spaceAfter=8,
        textColor=colors.HexColor("#003366"),
    )
    style_h3 = ParagraphStyle(
        "PolicyH3", parent=styles["Heading3"],
        fontSize=11, leading=14, spaceBefore=8, spaceAfter=6,
        textColor=colors.HexColor("#336699"),
    )
    style_body = ParagraphStyle(
        "PolicyBody", parent=styles["Normal"],
        fontSize=10, leading=14, spaceAfter=8, alignment=TA_JUSTIFY,
    )
    style_bullet = ParagraphStyle(
        "PolicyBullet", parent=style_body,
        leftIndent=20, bulletIndent=10,
        spaceBefore=2, spaceAfter=2,
    )
    style_footer = ParagraphStyle(
        "PolicyFooter", parent=styles["Normal"],
        fontSize=8, textColor=colors.grey, alignment=TA_CENTER,
    )

    def make_table(data, col_widths=None):
        """Create a styled table."""
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    def header_footer(canvas, doc, title, doc_id):
        """Draw header/footer on every page."""
        canvas.saveState()
        # Header
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(colors.HexColor("#003366"))
        canvas.drawString(72, 756, f"Maple Trust Bank — {doc_id}")
        canvas.drawRightString(540, 756, "CONFIDENTIAL")
        canvas.setStrokeColor(colors.HexColor("#003366"))
        canvas.line(72, 752, 540, 752)
        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(72, 30, f"Maple Trust Bank — {title}")
        canvas.drawRightString(540, 30, f"Page {doc.page}")
        canvas.line(72, 40, 540, 40)
        canvas.restoreState()

    def build_toc_entries(sections):
        """Build a simple table of contents from section headers."""
        elements = []
        elements.append(Paragraph("Table of Contents", style_h1))
        elements.append(Spacer(1, 10))
        for sec_num, sec_title, _ in sections:
            toc_style = ParagraphStyle(
                "TOC", parent=style_body,
                fontSize=10, leading=16, leftIndent=10 * (sec_num.count(".") if "." in sec_num else 0),
            )
            elements.append(Paragraph(f"{sec_num} {sec_title}", toc_style))
        elements.append(Spacer(1, 12))
        elements.append(PageBreak())
        return elements

    def build_section(sec_num, sec_title, content_items):
        """Build a section with heading and body content."""
        elements = []
        depth = sec_num.count(".")
        if depth == 0:
            elements.append(Paragraph(f"{sec_num}. {sec_title}", style_h1))
        elif depth == 1:
            elements.append(Paragraph(f"{sec_num} {sec_title}", style_h2))
        else:
            elements.append(Paragraph(f"{sec_num} {sec_title}", style_h3))

        for item in content_items:
            if isinstance(item, str):
                elements.append(Paragraph(item, style_body))
            elif isinstance(item, list):
                # It's table data
                elements.append(make_table(item))
                elements.append(Spacer(1, 8))
            elif isinstance(item, tuple) and item[0] == "bullet":
                for b in item[1]:
                    elements.append(Paragraph(f"\u2022 {b}", style_bullet))
            elif isinstance(item, tuple) and item[0] == "spacer":
                elements.append(Spacer(1, item[1]))
        return elements

    def build_pdf(filename, doc_id, title, version, effective_date, sections, target_pages=None):
        """Build a complete policy PDF."""
        filepath = policies_dir / filename
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            topMargin=1 * inch,
            bottomMargin=0.75 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )

        elements = []

        # Title page content
        elements.append(Spacer(1, 80))
        elements.append(Paragraph("MAPLE TRUST BANK", style_title))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(title, ParagraphStyle(
            "DocTitle", parent=style_title, fontSize=18, leading=22,
        )))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Document ID: {doc_id}", style_subtitle))
        elements.append(Paragraph(f"Version: {version}", style_subtitle))
        elements.append(Paragraph(f"Effective Date: {effective_date}", style_subtitle))
        elements.append(Paragraph("Classification: CONFIDENTIAL", style_subtitle))
        elements.append(Spacer(1, 20))

        # Document control table
        doc_control = [
            ["Document Control", ""],
            ["Document ID", doc_id],
            ["Title", title],
            ["Version", version],
            ["Effective Date", effective_date],
            ["Next Review Date", f"{int(effective_date[:4])+1}{effective_date[4:]}"],
            ["Classification", "CONFIDENTIAL"],
            ["Owner", "Chief Anti-Money Laundering Officer (CAMLO)"],
            ["Department", "AML Compliance"],
        ]
        elements.append(make_table(doc_control, col_widths=[180, 250]))
        elements.append(Spacer(1, 20))

        # Approval table
        approval_data = [
            ["Role", "Name", "Signature", "Date"],
            ["Chief Compliance Officer", "Sarah Chen", "S. Chen", effective_date],
            ["Chief Risk Officer", "Robert MacLeod", "R. MacLeod", effective_date],
            ["Head of AML Operations", "Priya Sharma", "P. Sharma", effective_date],
            ["SVP, Legal & Regulatory", "Jean-Pierre Tremblay", "J-P. Tremblay", effective_date],
        ]
        elements.append(make_table(approval_data, col_widths=[150, 120, 80, 80]))
        elements.append(Spacer(1, 20))

        # Version history table
        version_history = [
            ["Version", "Date", "Author", "Description of Changes"],
            ["1.0", "2020-01-15", "AML Compliance", "Initial policy creation"],
            ["1.5", "2021-06-01", "AML Compliance", "Updated for PCMLTFA amendments"],
            ["2.0", "2022-03-15", "AML Compliance", "Major revision — OSFI B-8 alignment"],
            [version, effective_date, "AML Compliance", "Current version — annual review update"],
        ]
        elements.append(Paragraph("Version History", style_h2))
        elements.append(make_table(version_history, col_widths=[60, 80, 100, 190]))
        elements.append(PageBreak())

        # TOC
        elements.extend(build_toc_entries(sections))

        # Body sections
        for sec_num, sec_title, content_items in sections:
            elements.extend(build_section(sec_num, sec_title, content_items))

        doc.build(
            elements,
            onFirstPage=lambda c, d: header_footer(c, d, title, doc_id),
            onLaterPages=lambda c, d: header_footer(c, d, title, doc_id),
        )
        return filepath

    # ---- Policy definitions ----
    # Each policy is: (filename, doc_id, title, version, effective_date, sections)
    # sections = [(sec_num, sec_title, [content_items])]

    policy_001_sections = [
        ("1", "Purpose and Scope", [
            "This policy establishes the framework for Maple Trust Bank's Anti-Money Laundering (AML) program in compliance with the Proceeds of Crime (Money Laundering) and Terrorist Financing Act (PCMLTFA), FINTRAC guidelines, and OSFI Guideline B-8.",
            "The AML program applies to all employees, contractors, and business partners of Maple Trust Bank across all branches, business lines, and subsidiaries operating within Canada and internationally.",
            ("bullet", [
                "All retail and commercial banking operations",
                "Wealth management and investment services",
                "Mortgage lending and credit facilities",
                "International wire transfer services",
                "Digital and mobile banking channels",
            ]),
            "This policy should be read in conjunction with MTB-POL-002 (KYC Procedures), MTB-POL-003 (Suspicious Transaction Reporting), and MTB-POL-006 (Transaction Monitoring Program).",
        ]),
        ("2", "Definitions", [
            [
                ["Term", "Definition"],
                ["AML", "Anti-Money Laundering — the set of procedures, laws, and regulations designed to prevent the practice of generating income through illegal actions."],
                ["FINTRAC", "Financial Transactions and Reports Analysis Centre of Canada — Canada's financial intelligence unit."],
                ["PCMLTFA", "Proceeds of Crime (Money Laundering) and Terrorist Financing Act — the primary Canadian AML legislation."],
                ["STR", "Suspicious Transaction Report — a report filed with FINTRAC when there are reasonable grounds to suspect ML/TF."],
                ["LCTR", "Large Cash Transaction Report — mandatory report for cash transactions of $10,000 CAD or more."],
                ["EFT", "Electronic Funds Transfer — includes domestic and international wire transfers."],
                ["ML/TF", "Money Laundering / Terrorist Financing."],
                ["PEP", "Politically Exposed Person — see MTB-POL-008 for detailed categories."],
                ["OSFI", "Office of the Superintendent of Financial Institutions — Canada's banking regulator."],
            ],
        ]),
        ("3", "Regulatory Framework", [
            "Maple Trust Bank's AML program is designed to comply with the following regulatory requirements:",
            ("bullet", [
                "Proceeds of Crime (Money Laundering) and Terrorist Financing Act (PCMLTFA), S.C. 2000, c. 17",
                "PCMLTFA Regulations, SOR/2002-184",
                "OSFI Guideline B-8: Deterring and Detecting Money Laundering and Terrorist Financing",
                "FINTRAC Guidance on Reporting and Record-Keeping",
                "Criminal Code of Canada, Part XII.2 — Proceeds of Crime",
                "United Nations Act and associated regulations for sanctions compliance",
            ]),
        ]),
        ("3.1", "Reporting Obligations", [
            "Under the PCMLTFA, Maple Trust Bank is required to file the following reports with FINTRAC:",
            [
                ["Report Type", "Threshold / Trigger", "Filing Deadline"],
                ["Large Cash Transaction Report (LCTR)", "$10,000 CAD or more in cash", "Within 15 calendar days"],
                ["Suspicious Transaction Report (STR)", "Reasonable grounds to suspect ML/TF", "Within 30 calendar days"],
                ["Electronic Funds Transfer Report (EFTR)", "$10,000 CAD or more (international)", "Within 5 business days"],
                ["Terrorist Property Report", "Property owned/controlled by listed entity", "Immediately upon discovery"],
                ["Casino Disbursement Report", "$10,000 CAD or more", "Within 15 calendar days"],
            ],
            "For detailed reporting procedures, see MTB-POL-003 (Suspicious Transaction Reporting Guidelines).",
        ]),
        ("4", "AML Program Governance", [
            "The AML program governance structure ensures accountability at all levels of the organization.",
        ]),
        ("4.1", "Chief Anti-Money Laundering Officer (CAMLO)", [
            "The CAMLO is the designated compliance officer responsible for the overall effectiveness of the AML program. The CAMLO reports directly to the Board of Directors through the Risk Committee.",
            ("bullet", [
                "Oversight of the AML compliance program",
                "Filing of STRs, LCTRs, and other mandatory reports with FINTRAC",
                "Annual AML risk assessment (see MTB-POL-010)",
                "Coordination with law enforcement agencies",
                "Reporting to the Board on AML program effectiveness",
                "Ensuring adequate resources for AML operations",
            ]),
        ]),
        ("4.2", "Three Lines of Defence", [
            [
                ["Line", "Responsibility", "Function"],
                ["First Line", "Business units and front-line staff", "Identify and report suspicious activities; perform CDD (MTB-POL-004)"],
                ["Second Line", "AML Compliance and Risk Management", "Policy development; transaction monitoring (MTB-POL-006); quality assurance"],
                ["Third Line", "Internal Audit", "Independent review of AML program effectiveness; regulatory compliance testing"],
            ],
        ]),
        ("5", "Risk-Based Approach", [
            "Maple Trust Bank adopts a risk-based approach (RBA) to AML compliance as required by FINTRAC and recommended by FATF. This approach ensures that resources are directed to areas of highest ML/TF risk.",
            "The risk assessment methodology is detailed in MTB-POL-010 (Risk Assessment Methodology) and considers the following risk categories:",
        ]),
        ("5.1", "Customer Risk Factors", [
            [
                ["Risk Factor", "Low Risk", "Medium Risk", "High Risk"],
                ["Customer Type", "Salaried individual", "Self-employed / SME", "Cash-intensive business / PEP"],
                ["Geographic Risk", "Domestic (Canada)", "US / EU / UK / Australia", "FATF high-risk jurisdiction"],
                ["Product Risk", "Standard savings account", "Investment account", "International wire / private banking"],
                ["Transaction Behaviour", "Consistent with profile", "Occasional anomaly", "Frequent large cash / structuring"],
                ["Source of Funds", "Employment income", "Business revenue", "Unknown / complex structures"],
            ],
            "Customers with elevated risk scores (70+) are subject to Enhanced Due Diligence (EDD) per MTB-POL-005.",
        ]),
        ("5.2", "Risk Scoring Model", [
            "Each customer receives a composite risk score from 1 to 100, calculated based on the weighted risk factors above. The scoring model is reviewed annually.",
            [
                ["Risk Score Range", "Risk Level", "Review Frequency", "EDD Required"],
                ["1-25", "Low", "Every 3 years", "No"],
                ["26-50", "Medium-Low", "Every 2 years", "No"],
                ["51-70", "Medium", "Annually", "No"],
                ["71-85", "High", "Semi-annually", "Yes (MTB-POL-005)"],
                ["86-100", "Very High", "Quarterly", "Yes — Senior Management approval"],
            ],
        ]),
        ("6", "Customer Due Diligence", [
            "Customer Due Diligence (CDD) is the cornerstone of Maple Trust Bank's AML program. Detailed CDD procedures are defined in MTB-POL-004.",
            ("bullet", [
                "Identity verification at account opening",
                "Ongoing monitoring of customer activity",
                "Periodic review based on risk level",
                "Enhanced due diligence for high-risk customers (MTB-POL-005)",
                "Sanctions screening at onboarding and on an ongoing basis (MTB-POL-007)",
                "PEP screening for all new and existing customers (MTB-POL-008)",
            ]),
        ]),
        ("7", "Transaction Monitoring", [
            "Maple Trust Bank maintains an automated transaction monitoring system to detect suspicious activities. The Transaction Monitoring Program is detailed in MTB-POL-006.",
            "Key monitoring scenarios include:",
            ("bullet", [
                "Large cash transactions at or near the $10,000 CAD reporting threshold",
                "Rapid movement of funds (in-and-out patterns)",
                "International wire transfers to/from high-risk jurisdictions",
                "Structuring (breaking large transactions into smaller amounts to avoid reporting)",
                "Unusual patterns inconsistent with customer profile",
                "Round-dollar transactions that may indicate layering",
                "Dormant account reactivation with sudden high activity",
            ]),
        ]),
        ("8", "Record Retention", [
            "All AML-related records must be retained in accordance with MTB-POL-009 (Record Retention and Data Management Policy). Key retention periods include:",
            [
                ["Record Type", "Retention Period", "Format"],
                ["Customer identification records", "5 years after account closure", "Digital / Physical"],
                ["Transaction records", "5 years from transaction date", "Digital"],
                ["STRs and supporting documentation", "5 years from filing date", "Digital — restricted access"],
                ["LCTRs", "5 years from filing date", "Digital"],
                ["Training records", "5 years", "Digital"],
                ["Risk assessments", "5 years from assessment date", "Digital"],
            ],
        ]),
        ("9", "Training and Awareness", [
            "All Maple Trust Bank employees must complete AML training within 30 days of hire and annually thereafter. Training content is tailored by role:",
            [
                ["Role Category", "Training Frequency", "Content Focus"],
                ["Front-line staff (tellers, CSRs)", "Semi-annually", "Red flags, customer identification, STR escalation"],
                ["Relationship managers", "Annually", "CDD/EDD procedures, PEP identification, risk assessment"],
                ["AML analysts", "Quarterly", "Advanced analytics, case management, regulatory updates"],
                ["Senior management", "Annually", "Governance, regulatory obligations, program oversight"],
                ["Board of Directors", "Annually", "Strategic AML risk, regulatory landscape, program effectiveness"],
            ],
        ]),
        ("10", "Monitoring, Testing, and Review", [
            "The AML program is subject to regular monitoring, testing, and review to ensure ongoing effectiveness.",
            ("bullet", [
                "Daily: Automated transaction monitoring alerts reviewed by AML analysts",
                "Monthly: AML Compliance team reviews key risk indicators (KRIs)",
                "Quarterly: CAMLO reports to Risk Committee on program performance",
                "Annually: Independent review of AML program by Internal Audit",
                "Biennially: External effectiveness review as required by PCMLTFA",
            ]),
        ]),
        ("11", "Appendix A — Glossary of Additional Terms", [
            [
                ["Term", "Definition"],
                ["Beneficial Owner", "Individual who ultimately owns or controls 25% or more of an entity"],
                ["Correspondent Banking", "Banking services provided by one bank to another"],
                ["FATF", "Financial Action Task Force — international AML standard-setter"],
                ["KYC", "Know Your Customer — identity verification and ongoing due diligence"],
                ["Shell Company", "A company with no significant assets or operations"],
                ["Smurfing", "Breaking large transactions into smaller ones to avoid reporting thresholds"],
                ["Layering", "The process of separating illicit funds from their source through complex transactions"],
            ],
        ]),
    ]

    policy_002_sections = [
        ("1", "Purpose", [
            "This document establishes the Know Your Customer (KYC) procedures for Maple Trust Bank in compliance with PCMLTFA requirements and FINTRAC guidance. KYC is a foundational element of the Bank's AML program (MTB-POL-001).",
            "Effective KYC procedures are essential for identifying and verifying the identity of customers, understanding their financial activities, and assessing the risk they pose to the Bank.",
        ]),
        ("2", "Scope", [
            "These procedures apply to all customer-facing activities across all business lines, channels (branch, online, mobile, ATM, phone), and subsidiaries of Maple Trust Bank.",
            ("bullet", [
                "New customer onboarding — retail, commercial, wealth, and institutional",
                "Ongoing customer relationship management",
                "Periodic reviews and re-verification",
                "Changes in customer circumstances or risk profile",
                "Account reopening after dormancy or closure",
            ]),
        ]),
        ("3", "Customer Identification Program (CIP)", [
            "All customers must be identified and verified before or during account opening. The CIP is the first step in the CDD process.",
        ]),
        ("3.1", "Individual Customers", [
            "For individual (natural person) customers, the following information must be collected and verified:",
            [
                ["Information", "Verification Method", "Acceptable Documents"],
                ["Full legal name", "Government-issued photo ID", "Passport, driver's licence, provincial ID"],
                ["Date of birth", "Government-issued photo ID", "Same as above"],
                ["Current residential address", "Utility bill, bank statement, CRA notice", "Dated within 90 days"],
                ["Occupation / Employment", "Self-declaration, employer letter", "Employment letter, business registration"],
                ["Canadian SIN (optional)", "SIN card / CRA documentation", "For tax reporting purposes only"],
            ],
            "At least one piece of government-issued photo identification must be verified. Dual identification is required for customers assessed as medium risk or higher.",
        ]),
        ("3.2", "Corporate and Institutional Customers", [
            "For corporate customers, the following must be obtained:",
            ("bullet", [
                "Certificate of Incorporation or Articles of Association",
                "Business registration number",
                "Names and addresses of all directors",
                "Identification of all beneficial owners holding 25% or more",
                "Nature and purpose of the business relationship",
                "Authorized signatories with specimen signatures",
                "Most recent audited financial statements (commercial and institutional segments)",
            ]),
            "Beneficial ownership verification is mandatory as per PCMLTFA requirements effective June 2021. See MTB-POL-004, Section 5.2 for detailed beneficial ownership procedures.",
        ]),
        ("4", "Customer Risk Assessment", [
            "Upon onboarding, each customer is assigned an initial risk rating based on the risk assessment methodology (MTB-POL-010). The risk rating determines the level of due diligence required.",
            [
                ["Risk Level", "CDD Level", "Review Cycle", "Approval Required"],
                ["Low (1-25)", "Standard CDD (MTB-POL-004)", "Every 3 years", "Branch Manager"],
                ["Medium (26-70)", "Standard CDD with enhanced monitoring", "Annually", "Compliance Officer"],
                ["High (71-85)", "Enhanced Due Diligence (MTB-POL-005)", "Semi-annually", "Senior Compliance Officer"],
                ["Very High (86-100)", "Enhanced Due Diligence + CAMLO review", "Quarterly", "CAMLO + Senior Management"],
            ],
        ]),
        ("5", "Ongoing KYC Obligations", [
            "KYC is not a one-time event. Maple Trust Bank maintains ongoing KYC obligations throughout the customer relationship.",
        ]),
        ("5.1", "Trigger Events for KYC Refresh", [
            "KYC must be refreshed when any of the following trigger events occur:",
            ("bullet", [
                "Material change in customer's occupation, business, or financial profile",
                "Customer requests new product or service inconsistent with existing profile",
                "Transaction monitoring alert generated for the customer (MTB-POL-006)",
                "Change in beneficial ownership structure",
                "Negative media screening results",
                "Customer identified as PEP or associate of PEP (MTB-POL-008)",
                "Address change to high-risk jurisdiction",
                "Risk score increases above a threshold boundary",
            ]),
        ]),
        ("5.2", "Periodic Review Schedule", [
            "In addition to trigger-based reviews, all customer files undergo periodic review:",
            [
                ["Customer Segment", "Low Risk", "Medium Risk", "High Risk"],
                ["Retail", "36 months", "12 months", "6 months"],
                ["Commercial", "24 months", "12 months", "6 months"],
                ["Wealth", "24 months", "12 months", "3 months"],
                ["Institutional", "12 months", "6 months", "3 months"],
            ],
        ]),
        ("6", "KYC Documentation Standards", [
            "All KYC documentation must meet the following standards:",
            ("bullet", [
                "Copies of identification documents must be clear and legible",
                "All documents must be dated and signed by the verifying officer",
                "Electronic verification results must be retained in the CRM system",
                "Physical documents must be scanned and uploaded within 5 business days",
                "All KYC records retained per MTB-POL-009 (minimum 5 years after relationship ends)",
            ]),
        ]),
        ("7", "Non-Face-to-Face Verification", [
            "For customers onboarded through digital channels (online, mobile), additional verification measures apply:",
            ("bullet", [
                "Two-factor authentication for identity verification",
                "Government-issued ID verification through approved digital verification service",
                "Credit bureau check as secondary verification",
                "Enhanced transaction monitoring for the first 90 days (MTB-POL-006)",
                "Video verification call for high-value accounts (investment, wealth)",
            ]),
            "Non-face-to-face onboarding may not be available for customers rated High or Very High risk at initial screening.",
        ]),
        ("8", "Roles and Responsibilities", [
            [
                ["Role", "KYC Responsibility"],
                ["Customer Service Representative", "Collect and verify customer identification; complete CIP forms"],
                ["Branch Manager", "Approve standard CDD; escalate medium/high risk cases"],
                ["Relationship Manager", "Ongoing monitoring; trigger-based KYC refresh; annual reviews"],
                ["Compliance Officer", "Approve medium-risk onboarding; review EDD referrals"],
                ["CAMLO", "Approve very high-risk relationships; oversight of KYC program"],
                ["Internal Audit", "Independent testing of KYC controls and procedures"],
            ],
        ]),
        ("9", "Exceptions and Escalation", [
            "Any exceptions to these KYC procedures must be documented and approved as follows:",
            [
                ["Exception Type", "Approval Authority", "Documentation Required"],
                ["Temporary ID shortfall (< 30 days)", "Branch Manager", "Exception form + follow-up date"],
                ["Extended ID shortfall (30-90 days)", "Compliance Officer", "Exception form + risk assessment"],
                ["Ongoing ID shortfall (> 90 days)", "CAMLO", "Full risk assessment + business justification"],
                ["Waiver of dual-ID requirement", "Senior Compliance Officer", "Alternative verification evidence"],
            ],
            "No customer account may remain open for more than 90 days without complete KYC verification unless expressly approved by the CAMLO with documented justification.",
        ]),
    ]

    policy_003_sections = [
        ("1", "Purpose", [
            "This document provides guidelines for the identification, assessment, and reporting of suspicious transactions at Maple Trust Bank. Suspicious Transaction Reports (STRs) are a critical component of Canada's AML/ATF regime under the PCMLTFA.",
            "All employees have a legal obligation to report transactions where there are reasonable grounds to suspect that the transaction is related to the commission of a money laundering or terrorist financing offence.",
        ]),
        ("2", "Scope", [
            "These guidelines apply to all Maple Trust Bank employees, agents, and third-party service providers involved in processing, monitoring, or overseeing customer transactions across all channels and products.",
        ]),
        ("3", "Reporting Thresholds and Requirements", [
        ]),
        ("3.1", "Large Cash Transaction Reports (LCTRs)", [
            "A Large Cash Transaction Report must be filed with FINTRAC for any cash transaction (receipt) of $10,000 CAD or more, or multiple cash transactions within a 24-hour period that total $10,000 CAD or more from the same individual.",
            [
                ["Scenario", "Report Required", "Deadline"],
                ["Single cash deposit >= $10,000 CAD", "LCTR", "15 calendar days"],
                ["Multiple cash deposits totalling >= $10,000 in 24 hrs (same person)", "LCTR", "15 calendar days"],
                ["Cash withdrawal >= $10,000 CAD", "Not reportable as LCTR", "N/A — but may trigger STR"],
                ["Foreign currency cash equivalent to >= $10,000 CAD", "LCTR", "15 calendar days"],
            ],
        ]),
        ("3.2", "Suspicious Transaction Reports (STRs)", [
            "An STR must be filed with FINTRAC when there are reasonable grounds to suspect that a transaction or attempted transaction is related to money laundering or terrorist financing. There is no monetary threshold for STRs.",
            "Key principles for STR filing:",
            ("bullet", [
                "No minimum dollar amount — any transaction amount may be suspicious",
                "Attempted transactions must also be reported if suspicious",
                "The suspicion must be based on reasonable grounds, not certainty",
                "Tipping off the customer is strictly prohibited under Section 7 of the PCMLTFA",
                "STRs must be filed within 30 calendar days of the determination of suspicion",
                "All supporting documentation must be retained for 5 years (MTB-POL-009)",
            ]),
        ]),
        ("3.3", "International Electronic Funds Transfer Reports", [
            "International Electronic Funds Transfer Reports (IEFTRs) must be filed for international EFTs of $10,000 CAD or more.",
            ("bullet", [
                "Incoming international EFTs >= $10,000 CAD",
                "Outgoing international EFTs >= $10,000 CAD",
                "Filing deadline: 5 business days",
                "Travel rule information must accompany all EFTs >= $1,000 CAD",
            ]),
        ]),
        ("4", "Red Flag Indicators", [
            "The following are common red flag indicators that may warrant further investigation and potential STR filing. This list is not exhaustive.",
        ]),
        ("4.1", "Customer Behaviour Red Flags", [
            ("bullet", [
                "Customer appears nervous, evasive, or refuses to provide information",
                "Customer insists on conducting transactions just below reporting thresholds",
                "Customer conducts transactions inconsistent with their profile or stated purpose",
                "Customer shows unusual knowledge of AML reporting requirements",
                "Customer uses multiple identifications with inconsistent information",
                "Customer makes frequent changes to account structure or beneficial ownership",
                "Customer refuses to provide source of funds information",
                "Customer requests that transactions be processed to avoid record-keeping",
            ]),
        ]),
        ("4.2", "Transaction Red Flags", [
            [
                ["Red Flag Category", "Examples"],
                ["Structuring", "Multiple deposits just under $10,000; use of multiple branches for similar amounts"],
                ["Rapid movement", "Large deposits followed by immediate withdrawals or wire transfers"],
                ["Unusual patterns", "Round-dollar amounts; transactions inconsistent with business type"],
                ["Geographic risk", "Wires to/from sanctioned countries or known ML jurisdictions"],
                ["Third-party involvement", "Third parties depositing to customer's account without explanation"],
                ["Dormant account activity", "Sudden reactivation of dormant accounts with large transactions"],
                ["Cash-intensive", "Business deposits significantly higher than industry norms"],
            ],
        ]),
        ("5", "STR Filing Process", [
            "The STR filing process follows the workflow described below. See MTB-POL-006 for transaction monitoring alert handling.",
        ]),
        ("5.1", "Detection and Initial Assessment", [
            ("bullet", [
                "Step 1: Suspicious activity detected by front-line staff or transaction monitoring system (MTB-POL-006)",
                "Step 2: Initial assessment by detecting employee — document observations",
                "Step 3: Complete internal Suspicious Activity Referral Form (SARF)",
                "Step 4: Submit SARF to branch Compliance Officer within 24 hours",
            ]),
        ]),
        ("5.2", "Investigation and Decision", [
            ("bullet", [
                "Step 5: Compliance Officer reviews SARF and supporting transaction data",
                "Step 6: Additional investigation as needed (customer file review, previous alerts)",
                "Step 7: Decision to file STR or close with documented rationale",
                "Step 8: If STR warranted, forward to CAMLO for final review",
                "Step 9: CAMLO approves and files STR with FINTRAC via F2R system",
                "Step 10: Case documented in AML case management system",
            ]),
        ]),
        ("6", "Tipping Off Prohibition", [
            "Section 7 of the PCMLTFA strictly prohibits disclosure of the existence or contents of an STR to the subject of the report or any third party not authorized to receive such information.",
            "Violation of the tipping-off prohibition is a criminal offence punishable by imprisonment of up to 2 years.",
            ("bullet", [
                "Do not inform the customer that an STR has been filed or is being considered",
                "Do not discuss STR details with colleagues who do not have a need to know",
                "Do not refuse service to a customer solely because an STR has been filed — this may constitute tipping off",
                "If a customer inquires about account restrictions, refer to standard compliance procedures without mentioning STRs",
            ]),
        ]),
        ("7", "Quality Assurance and Metrics", [
            "The AML Compliance team tracks the following metrics to ensure STR program effectiveness:",
            [
                ["Metric", "Target", "Reporting Frequency"],
                ["STR filing rate (% of SARFs resulting in STR)", ">= 30%", "Monthly"],
                ["Average time from detection to filing", "<= 20 calendar days", "Monthly"],
                ["STR rejection rate by FINTRAC", "< 5%", "Quarterly"],
                ["False positive rate (transaction monitoring)", "< 95%", "Monthly"],
                ["Employee awareness test scores", ">= 85%", "Annually"],
            ],
        ]),
        ("8", "Roles and Responsibilities", [
            [
                ["Role", "Responsibility"],
                ["All employees", "Detect and report suspicious activity via SARF"],
                ["Branch Compliance Officer", "Initial review of SARFs; quality check; escalation"],
                ["AML Analyst", "Detailed investigation; case documentation"],
                ["CAMLO", "Final STR approval; FINTRAC filing; program oversight"],
                ["Internal Audit", "Independent testing of STR process effectiveness"],
            ],
        ]),
    ]

    policy_004_sections = [
        ("1", "Purpose", [
            "This document defines the Customer Due Diligence (CDD) standards for Maple Trust Bank, implementing the requirements of the PCMLTFA and FINTRAC guidance on CDD obligations.",
            "CDD is the process through which the Bank verifies the identity of customers, understands their financial dealings, and assesses the risk they present. These standards complement the KYC procedures (MTB-POL-002) and AML program policy (MTB-POL-001).",
        ]),
        ("2", "CDD Requirements by Customer Type", [
            [
                ["Customer Type", "Standard CDD", "EDD Trigger"],
                ["Individual — Retail", "Government ID + address verification", "Risk score >= 71 or PEP (MTB-POL-008)"],
                ["Individual — Wealth", "Dual ID + source of wealth", "All wealth clients >= $1M AUM"],
                ["Corporate — SME", "Business registration + beneficial ownership", "Cash-intensive business or high-risk sector"],
                ["Corporate — Large", "Full corporate docs + BO + audited financials", "Complex ownership or foreign control"],
                ["Institutional", "Regulatory status + authorized signatories", "Non-regulated or foreign institution"],
            ],
        ]),
        ("3", "Standard CDD Procedures", [
            "Standard CDD must be completed for all new customer relationships and consists of the following elements:",
        ]),
        ("3.1", "Identity Verification", [
            "Identity verification must be completed before or at account opening. Acceptable methods include:",
            ("bullet", [
                "In-person verification of government-issued photo ID",
                "Credit bureau verification (Equifax or TransUnion)",
                "Digital identity verification through approved service provider",
                "Dual-process method: confirming identity through two independent sources",
            ]),
            "All verification must be documented in the CRM system with date, method, and verifying officer. See MTB-POL-002, Section 3 for detailed CIP requirements.",
        ]),
        ("3.2", "Purpose and Nature of Relationship", [
            "The purpose and intended nature of the business relationship must be documented. For retail customers, this includes understanding the expected types of transactions, frequency, and volume. For commercial customers, this additionally includes understanding the nature of the business and its customer base.",
        ]),
        ("4", "Ongoing CDD", [
            "CDD is an ongoing obligation. Transaction monitoring (MTB-POL-006) forms the automated component of ongoing CDD, supplemented by periodic manual reviews.",
            ("bullet", [
                "Monitor transactions against customer profile",
                "Update customer information at scheduled review intervals",
                "Re-assess risk score upon trigger events (MTB-POL-002, Section 5.1)",
                "Screen against updated sanctions lists (MTB-POL-007)",
                "Review negative media results from screening vendor",
            ]),
        ]),
        ("5", "Beneficial Ownership", [
        ]),
        ("5.1", "Definition and Thresholds", [
            "A beneficial owner is any individual who directly or indirectly owns or controls 25% or more of an entity, or any individual who exerts significant control over the entity.",
            "For trusts: the settlor, trustees, beneficiaries, and any person who holds a power of appointment must be identified.",
        ]),
        ("5.2", "Verification Procedures", [
            "Beneficial ownership must be verified through:",
            ("bullet", [
                "Corporate registry searches (federal and provincial)",
                "Annual return filings",
                "Shareholder registers and partnership agreements",
                "Trust deeds and declarations of trust",
                "Self-declaration by the entity, confirmed by documentary evidence",
            ]),
            "Where the beneficial ownership structure is complex (multiple layers, foreign entities, nominee arrangements), Enhanced Due Diligence applies per MTB-POL-005.",
        ]),
        ("6", "CDD for Specific Products", [
            [
                ["Product", "Additional CDD Requirements"],
                ["Mortgage", "Property valuation; source of down payment; employment/income verification"],
                ["Investment Account", "Investment knowledge assessment; risk tolerance; source of initial deposit"],
                ["Credit Card", "Credit bureau check; income verification; employment confirmation"],
                ["International Wire Services", "Purpose of transfers; beneficiary relationship; country risk assessment"],
                ["Private Banking / Wealth", "Full source of wealth; net worth declaration; EDD per MTB-POL-005"],
            ],
        ]),
        ("7", "Record-Keeping Requirements", [
            "All CDD records must be retained in accordance with MTB-POL-009. Key requirements:",
            ("bullet", [
                "Customer identification records: 5 years after account closure",
                "Transaction records: 5 years from date of transaction",
                "Risk assessments: 5 years from date of assessment",
                "Beneficial ownership records: 5 years after relationship end",
                "All records must be accessible within 30 days of a FINTRAC request",
            ]),
        ]),
        ("8", "Failure to Complete CDD", [
            "If CDD cannot be satisfactorily completed, the Bank must:",
            ("bullet", [
                "Not open the account or establish the business relationship",
                "Consider filing an STR if the inability to complete CDD raises suspicion (MTB-POL-003)",
                "Document the reason for the inability to complete CDD",
                "For existing relationships: consider whether to maintain the relationship",
            ]),
            "Existing accounts where CDD cannot be updated must be escalated to the Compliance Officer for review within 10 business days.",
        ]),
        ("9", "Roles and Responsibilities", [
            [
                ["Role", "CDD Responsibility"],
                ["Customer Service Representative", "Collect required CDD documentation; initial verification"],
                ["Relationship Manager", "Ongoing CDD; periodic reviews; escalation of changes"],
                ["Branch Manager", "Approve standard-risk relationships; ensure branch CDD compliance"],
                ["Compliance Officer", "Review medium/high-risk CDD; approve exceptions"],
                ["CAMLO", "Oversight of CDD program; approve very high-risk relationships"],
            ],
        ]),
    ]

    policy_005_sections = [
        ("1", "Purpose", [
            "This document outlines the Enhanced Due Diligence (EDD) standards for high-risk customers at Maple Trust Bank. EDD supplements the standard CDD procedures (MTB-POL-004) with additional scrutiny for customers that present elevated ML/TF risk.",
            "EDD is required by the PCMLTFA for prescribed categories of high-risk customers and is a key component of the Bank's risk-based approach (MTB-POL-001, Section 5).",
        ]),
        ("2", "When EDD is Required", [
            "EDD must be applied in the following circumstances:",
            [
                ["Trigger", "Reference", "EDD Level"],
                ["Customer risk score >= 71", "MTB-POL-010", "Standard EDD"],
                ["Politically Exposed Person (PEP)", "MTB-POL-008", "PEP EDD"],
                ["Customer in high-risk jurisdiction", "FATF list", "Geographic EDD"],
                ["Complex ownership structure", "MTB-POL-004, Section 5", "Ownership EDD"],
                ["Cash-intensive business", "MTB-POL-010", "Standard EDD"],
                ["Correspondent banking relationship", "OSFI B-8", "Correspondent EDD"],
                ["Customer risk score >= 86", "MTB-POL-010", "Standard EDD + CAMLO approval"],
                ["Wealth management client >= $1M AUM", "Internal policy", "Wealth EDD"],
            ],
        ]),
        ("3", "EDD Procedures", [
        ]),
        ("3.1", "Additional Information Collection", [
            "Beyond standard CDD, the following additional information must be obtained for EDD customers:",
            ("bullet", [
                "Detailed source of wealth and source of funds documentation",
                "Purpose of complex transactions and expected transaction patterns",
                "References from other financial institutions (where applicable)",
                "Background checks through approved third-party provider",
                "Enhanced media screening (multiple languages if applicable)",
                "Verification of all beneficial owners regardless of ownership percentage",
            ]),
        ]),
        ("3.2", "Senior Management Approval", [
            "The onboarding and continued maintenance of EDD customers requires senior management approval:",
            [
                ["Risk Level", "Approval Authority", "Review and Renewal"],
                ["High (71-85)", "Senior Compliance Officer", "Semi-annually"],
                ["Very High (86-100)", "CAMLO + SVP Risk", "Quarterly"],
                ["PEP — Domestic", "CAMLO", "Annually"],
                ["PEP — Foreign", "CAMLO + SVP Risk", "Semi-annually"],
                ["Head of International Organization", "CAMLO + EVP + Board notification", "Semi-annually"],
            ],
        ]),
        ("4", "Enhanced Transaction Monitoring for EDD Customers", [
            "EDD customers are subject to enhanced transaction monitoring thresholds under MTB-POL-006:",
            ("bullet", [
                "Automated alerts at 50% of standard thresholds",
                "Daily review of all wire transfers",
                "Weekly review of cash transactions",
                "Monthly compliance officer review of overall account activity",
                "Immediate alert for any transaction with sanctioned country nexus (MTB-POL-007)",
            ]),
        ]),
        ("5", "EDD Documentation Requirements", [
            "EDD case files must include:",
            ("bullet", [
                "Completed EDD assessment form",
                "Source of wealth and source of funds evidence",
                "Senior management approval documentation",
                "Risk assessment with rationale for risk rating",
                "Ongoing monitoring plan with specific triggers",
                "All previous periodic review reports",
                "Any STRs filed (reference numbers only, with access restricted per MTB-POL-003)",
            ]),
            "All EDD records are retained for 5 years after the relationship ends per MTB-POL-009.",
        ]),
        ("6", "Exit Procedures", [
            "If the Bank decides to exit a high-risk customer relationship, the following procedures apply:",
            ("bullet", [
                "Decision must be documented with rationale",
                "Consideration of whether to file an STR (MTB-POL-003)",
                "Customer notification in accordance with account terms — no reference to AML concerns",
                "Orderly wind-down of the relationship",
                "Retention of all CDD/EDD records per MTB-POL-009",
            ]),
        ]),
    ]

    policy_006_sections = [
        ("1", "Purpose", [
            "This document defines Maple Trust Bank's Transaction Monitoring Program, which forms a critical component of the Bank's AML compliance framework (MTB-POL-001). The program utilizes automated systems and manual processes to detect potentially suspicious transaction activity.",
        ]),
        ("2", "Scope", [
            "The transaction monitoring program covers all customer transactions across all channels (branch, online, mobile, ATM, phone), products, and currencies processed through Maple Trust Bank systems.",
            "This includes transactions in CAD, USD, EUR, GBP, and all other currencies in which the Bank transacts.",
        ]),
        ("3", "Monitoring System Architecture", [
            "The Bank's transaction monitoring system operates in real-time and batch modes:",
            [
                ["Component", "Mode", "Function", "Data Source"],
                ["Rule-based engine", "Batch (daily)", "Scenario-based detection", "Core banking transactions"],
                ["ML anomaly detection", "Batch (daily)", "Behavioural anomaly scoring", "Transaction history + customer profile"],
                ["Real-time screening", "Real-time", "Sanctions and PEP screening", "Wire transfer messages"],
                ["Network analytics", "Weekly batch", "Relationship pattern detection", "Transaction counterparty network"],
            ],
            "The monitoring system processes data from the Bank's core banking platform, wire transfer system, and card processing network. Data integration follows the lineage framework documented in the Bank's data architecture standards.",
        ]),
        ("4", "Monitoring Scenarios", [
            "The following monitoring scenarios are implemented. Thresholds are reviewed and updated semi-annually by the AML Compliance team.",
        ]),
        ("4.1", "Cash Transaction Monitoring", [
            [
                ["Scenario ID", "Scenario Description", "Threshold", "Alert Priority"],
                ["TM-001", "Single large cash transaction", ">= $10,000 CAD", "Medium — auto-generates LCTR"],
                ["TM-002", "Aggregate cash in 24 hours (same customer)", ">= $10,000 CAD", "Medium — auto-generates LCTR"],
                ["TM-003", "Cash transactions just below threshold", "$8,000-$9,999 (3+ occurrences in 7 days)", "High — potential structuring"],
                ["TM-004", "Cash deposits inconsistent with profile", "> 200% of expected monthly average", "Medium"],
            ],
        ]),
        ("4.2", "Wire Transfer Monitoring", [
            [
                ["Scenario ID", "Scenario Description", "Threshold", "Alert Priority"],
                ["TM-005", "International wire to high-risk jurisdiction", "Any amount", "High"],
                ["TM-006", "Large international wire", ">= $50,000 CAD equivalent", "Medium"],
                ["TM-007", "Rapid wire transfer pattern (in-and-out)", "Wire out within 48 hours of deposit", "High"],
                ["TM-008", "Multiple wires to same beneficiary", "3+ wires to same entity in 30 days", "Medium"],
            ],
        ]),
        ("4.3", "Account Activity Monitoring", [
            [
                ["Scenario ID", "Scenario Description", "Threshold", "Alert Priority"],
                ["TM-009", "Dormant account reactivation", "No activity for 12+ months then transaction", "Medium"],
                ["TM-010", "Unusual transaction volume spike", "> 300% of 6-month average transaction count", "Medium"],
                ["TM-011", "Round-dollar transactions", "5+ round-dollar amounts in 30 days", "Low"],
                ["TM-012", "Third-party deposits", "Deposits from non-account holders", "Medium"],
            ],
        ]),
        ("5", "Alert Management", [
        ]),
        ("5.1", "Alert Prioritization", [
            "Alerts are prioritized based on risk level and scenario type:",
            [
                ["Priority", "Response Time", "Disposition Options"],
                ["Critical", "Same business day", "Escalate, Investigate, File STR"],
                ["High", "2 business days", "Investigate, Escalate, Close with rationale"],
                ["Medium", "5 business days", "Review, Investigate, Close with rationale"],
                ["Low", "10 business days", "Review, Close with rationale"],
            ],
        ]),
        ("5.2", "Alert Investigation Workflow", [
            ("bullet", [
                "Step 1: Alert received in case management system — auto-assigned to analyst",
                "Step 2: Initial triage — analyst reviews transaction details and customer profile",
                "Step 3: Investigation — gather supporting information, review prior alerts",
                "Step 4: Assessment — determine if suspicious activity (see MTB-POL-003 red flags)",
                "Step 5: Disposition — close alert or escalate for STR consideration",
                "Step 6: Documentation — complete investigation notes and rationale",
                "Step 7: Quality review — supervisor reviews a sample of closed alerts",
            ]),
        ]),
        ("6", "Model Governance", [
            "The ML-based anomaly detection models used in transaction monitoring are subject to the Bank's model risk management framework:",
            ("bullet", [
                "Annual model validation by independent model risk team",
                "Quarterly model performance review (precision, recall, false positive rates)",
                "Semi-annual threshold calibration based on detection effectiveness",
                "Change management process for all model updates",
                "Complete model documentation including training data, features, and decision logic",
            ]),
        ]),
        ("7", "Data Quality and Integration", [
            "The effectiveness of transaction monitoring depends on data quality. The following standards apply:",
            ("bullet", [
                "Transaction data must be complete — missing fields generate data quality alerts",
                "Customer profile data must be current — stale profiles (not updated per MTB-POL-002 schedule) are flagged",
                "Data lineage must be documented per the Bank's data governance framework",
                "Data reconciliation between source systems and monitoring platform: daily",
                "Monitoring system uptime SLA: 99.5%",
            ]),
        ]),
        ("8", "Reporting and Metrics", [
            [
                ["Metric", "Target", "Reporting"],
                ["Alert volume by scenario", "Tracked (no target)", "Daily dashboard"],
                ["Alert disposition time (average)", "Within SLA per priority", "Weekly"],
                ["False positive rate", "< 90%", "Monthly"],
                ["STR conversion rate", ">= 5% of investigated alerts", "Monthly"],
                ["Scenario coverage (% of FINTRAC typologies)", ">= 90%", "Semi-annually"],
                ["Model performance (AUC)", ">= 0.75", "Quarterly"],
            ],
        ]),
    ]

    policy_007_sections = [
        ("1", "Purpose", [
            "This document establishes the procedures for sanctions screening at Maple Trust Bank in compliance with Canadian sanctions legislation, UN Security Council resolutions, and OSFI expectations.",
            "Sanctions screening is a critical control to ensure the Bank does not process transactions or maintain relationships with sanctioned individuals, entities, or countries.",
        ]),
        ("2", "Regulatory Framework", [
            "Maple Trust Bank's sanctions program complies with:",
            ("bullet", [
                "United Nations Act (Canada)",
                "Special Economic Measures Act (SEMA)",
                "Justice for Victims of Corrupt Foreign Officials Act (Sergei Magnitsky Law)",
                "Criminal Code of Canada — Terrorist Financing provisions",
                "OSFI Advisory on Economic Sanctions",
                "OFAC (US) regulations where applicable to USD transactions",
            ]),
        ]),
        ("3", "Screening Requirements", [
            [
                ["Screening Event", "Lists Screened", "Frequency"],
                ["Customer onboarding", "All consolidated lists", "At account opening"],
                ["Periodic rescreening", "All consolidated lists", "Daily batch"],
                ["Wire transfer — outgoing", "All lists + OFAC (for USD)", "Real-time"],
                ["Wire transfer — incoming", "All lists", "Real-time"],
                ["Trade finance transactions", "All lists + vessel/entity lists", "Per transaction"],
                ["List updates", "Updated list against customer base", "Within 24 hours of list publication"],
            ],
        ]),
        ("4", "Sanctions Lists", [
            "The Bank screens against the following consolidated sanctions lists:",
            ("bullet", [
                "Canadian Consolidated Autonomous Sanctions List (CCASL)",
                "United Nations Security Council Consolidated List",
                "OSFI Consolidated List of Sanctioned Entities",
                "OFAC Specially Designated Nationals (SDN) List — for USD transactions",
                "EU Consolidated List — for EUR transactions",
                "UK HM Treasury Sanctions List — for GBP transactions",
            ]),
            "Lists are updated in the screening system within 24 hours of publication by the relevant authority.",
        ]),
        ("5", "Screening Process", [
        ]),
        ("5.1", "Automated Screening", [
            "The Bank's automated screening system uses fuzzy matching algorithms to compare customer data against sanctions lists. The system is configured with the following match sensitivity:",
            [
                ["Matching Parameter", "Setting"],
                ["Name matching threshold", ">= 85% similarity"],
                ["Alias matching", "Enabled — all known aliases"],
                ["Date of birth matching", "Exact or +/- 2 years"],
                ["Country matching", "Included in scoring"],
                ["Phonetic matching", "Soundex and Double Metaphone"],
            ],
        ]),
        ("5.2", "Alert Disposition", [
            "Sanctions screening alerts are classified and dispositioned as follows:",
            ("bullet", [
                "True Match: Confirmed match to sanctioned entity — immediately escalate to CAMLO and legal; freeze assets",
                "Potential Match: Requires additional investigation — resolve within 4 business hours for wire transfers",
                "False Positive: Confirmed not a match — document rationale and close",
            ]),
            "All true matches must be reported to FINTRAC as Terrorist Property Reports and to OSFI immediately.",
        ]),
        ("6", "Sanctioned Country Restrictions", [
            "Maple Trust Bank does not process transactions to or from comprehensively sanctioned jurisdictions. Partial sanctions require transaction-level review per the applicable sanctions regime.",
            "The list of sanctioned jurisdictions is maintained by the Compliance team and updated per Canadian government publications.",
        ]),
        ("7", "Roles and Responsibilities", [
            [
                ["Role", "Sanctions Responsibility"],
                ["Sanctions Screening Analyst", "Review and disposition automated alerts"],
                ["Wire Transfer Operations", "Ensure all wires screened before release"],
                ["Compliance Officer", "Oversee sanctions screening program; investigate potential matches"],
                ["CAMLO", "Escalation point for true matches; FINTRAC/OSFI reporting"],
                ["Legal Counsel", "Advise on sanctions obligations; liaise with government agencies"],
            ],
        ]),
    ]

    policy_008_sections = [
        ("1", "Purpose", [
            "This policy establishes Maple Trust Bank's procedures for identifying, screening, and managing relationships with Politically Exposed Persons (PEPs), their family members, and close associates, as required by the PCMLTFA.",
        ]),
        ("2", "PEP Categories", [
            "The PCMLTFA defines the following categories of PEPs:",
            [
                ["Category", "Definition", "Examples"],
                ["Domestic PEP", "Person who holds or has held a prescribed position in Canada", "Members of Parliament, Senators, Mayors of major cities, Deputy Ministers, Judges of superior courts, Heads of Crown corporations"],
                ["Foreign PEP", "Person who holds or has held a prescribed position in a foreign state", "Heads of state, Cabinet ministers, Senior military officers, Judges of supreme/constitutional courts, Ambassadors"],
                ["Head of International Organization (HIO)", "Person who is head of an international organization established by governments", "UN Secretary-General, World Bank President, IMF Managing Director, NATO Secretary-General"],
                ["PEP Family Member", "Spouse, child, parent, sibling of a PEP", "As defined in PCMLTFA regulations"],
                ["Close Associate", "Person closely associated with a PEP for personal or business reasons", "Business partners, legal advisors, persons in financial arrangements with PEP"],
            ],
        ]),
        ("3", "PEP Screening Procedures", [
            "All customers must be screened for PEP status at onboarding and on an ongoing basis.",
            ("bullet", [
                "Initial screening at account opening — automated against PEP databases",
                "Ongoing batch screening — daily against updated PEP lists",
                "Self-declaration — customers must declare PEP status on account application",
                "Negative media screening — for PEP-associated adverse media",
                "Domestic PEPs: determination required for all customers",
                "Foreign PEPs: determination required for all customers (enhanced measures apply)",
            ]),
        ]),
        ("4", "CDD Requirements for PEPs", [
            [
                ["PEP Type", "CDD Requirement", "Approval Level", "Review Frequency"],
                ["Domestic PEP", "EDD per MTB-POL-005", "Senior Compliance Officer", "Annually"],
                ["Foreign PEP", "EDD + source of wealth + senior management approval", "CAMLO + SVP Risk", "Semi-annually"],
                ["HIO", "EDD + Board notification", "CAMLO + EVP", "Semi-annually"],
                ["Family Member / Close Associate", "Same as associated PEP category", "Same as associated PEP", "Same as associated PEP"],
            ],
        ]),
        ("5", "PEP De-listing", [
            "A person ceases to be a PEP classification under the following conditions:",
            ("bullet", [
                "Domestic PEP: 5 years after leaving the prescribed position (per PCMLTFA)",
                "Foreign PEP: The Bank maintains PEP classification indefinitely for foreign PEPs",
                "HIO: 5 years after leaving the position",
                "Family members and close associates: when the associated person is de-listed",
            ]),
            "De-listing requires Compliance Officer approval and documentation. Risk-based monitoring may continue beyond de-listing.",
        ]),
        ("6", "Record-Keeping", [
            "PEP screening results, determinations, and related documentation must be retained per MTB-POL-009. All PEP records must be accessible within 30 days of a FINTRAC request.",
        ]),
    ]

    policy_009_sections = [
        ("1", "Purpose", [
            "This policy defines the record retention and data management requirements for Maple Trust Bank in compliance with the PCMLTFA, OSFI guidelines, and applicable privacy legislation (PIPEDA).",
            "Proper record retention ensures the Bank can meet its regulatory obligations, support investigations, and respond to requests from FINTRAC, law enforcement, and other authorities.",
        ]),
        ("2", "Scope", [
            "This policy applies to all records created, received, maintained, or transmitted by Maple Trust Bank in the course of its business operations, including:",
            ("bullet", [
                "Customer identification and KYC records (MTB-POL-002)",
                "Transaction records and supporting documentation",
                "AML/ATF compliance records (STRs, LCTRs, EFTRs)",
                "CDD and EDD assessment records (MTB-POL-004, MTB-POL-005)",
                "Sanctions screening records (MTB-POL-007)",
                "PEP determination records (MTB-POL-008)",
                "Risk assessment records (MTB-POL-010)",
                "Training and awareness records",
            ]),
        ]),
        ("3", "Retention Periods", [
            [
                ["Record Category", "Retention Period", "Trigger Date", "Storage"],
                ["Customer identification (ID copies, verification)", "5 years", "After account closure / last transaction", "Secure digital archive"],
                ["Transaction records (all types)", "5 years", "From date of transaction", "Data warehouse"],
                ["STR and supporting documents", "5 years", "From date of filing", "Restricted access — AML system"],
                ["LCTR records", "5 years", "From date of filing", "Compliance system"],
                ["IEFTR records", "5 years", "From date of filing", "Compliance system"],
                ["CDD/EDD assessment files", "5 years", "After relationship ends", "CRM / compliance system"],
                ["Risk assessments", "5 years", "From date of assessment", "Risk management system"],
                ["Sanctions screening results", "5 years", "From date of screening", "Compliance system"],
                ["PEP determinations", "5 years", "After de-listing or relationship end", "Compliance system"],
                ["Training records", "5 years", "From date of training completion", "HR system"],
                ["Board and committee minutes (AML-related)", "10 years", "From date of meeting", "Corporate secretary"],
                ["Audit reports (AML)", "7 years", "From date of report", "Internal audit system"],
                ["Correspondence with regulators", "10 years", "From date of correspondence", "Legal / compliance"],
            ],
        ]),
        ("4", "Data Management Standards", [
        ]),
        ("4.1", "Data Classification", [
            [
                ["Classification", "Description", "Access Control", "Examples"],
                ["Restricted", "Highly sensitive — regulatory/legal significance", "Role-based, need-to-know, encrypted", "STRs, law enforcement requests, CAMLO files"],
                ["Confidential", "Sensitive business and customer data", "Role-based access, encrypted at rest", "Customer PII, transaction data, risk scores"],
                ["Internal", "Business information not for public disclosure", "All employees with business need", "Policies, procedures, training materials"],
                ["Public", "Information approved for public release", "No restriction", "Marketing materials, published rates"],
            ],
        ]),
        ("4.2", "Data Quality Requirements", [
            "All records must meet the following quality standards:",
            ("bullet", [
                "Completeness — all required fields populated",
                "Accuracy — verified against source documents",
                "Timeliness — records created or updated within defined SLAs",
                "Consistency — uniform formats across systems",
                "Accessibility — retrievable within 30 days for regulatory requests",
                "Integrity — tamper-evident storage with audit trails",
            ]),
        ]),
        ("5", "Data Lifecycle Management", [
            ("bullet", [
                "Creation: Records created as part of business processes per applicable policies",
                "Active Use: Records available in primary systems for business operations",
                "Archival: Records moved to archive storage after active use period",
                "Retention: Records maintained in archive for required retention period",
                "Destruction: Records securely destroyed after retention period expires",
            ]),
            "No records may be destroyed if they are subject to a legal hold, regulatory inquiry, or ongoing investigation.",
        ]),
        ("6", "Privacy and Cross-Border Considerations", [
            "Record retention must comply with PIPEDA and provincial privacy legislation. Customer personal information may only be retained for the purposes for which it was collected, or as required by law.",
            ("bullet", [
                "Customer consent for data retention must be documented",
                "Cross-border data transfers must comply with PIPEDA adequacy requirements",
                "Data stored outside Canada must be subject to equivalent protection standards",
                "Right of access requests from customers must be responded to within 30 days",
            ]),
        ]),
        ("7", "Secure Destruction", [
            "When records reach the end of their retention period and are not subject to any hold, they must be securely destroyed:",
            [
                ["Format", "Destruction Method", "Certification"],
                ["Physical documents", "Cross-cut shredding (DIN 66399 Level P-4 minimum)", "Certificate of destruction"],
                ["Digital records — standard", "Secure deletion with overwrite (NIST 800-88)", "Deletion log with timestamp"],
                ["Digital records — restricted", "Cryptographic erasure or physical media destruction", "Certificate of destruction"],
                ["Backup media", "Degaussing or physical destruction", "Certificate of destruction"],
            ],
        ]),
    ]

    policy_010_sections = [
        ("1", "Purpose", [
            "This document defines Maple Trust Bank's risk assessment methodology for ML/TF risk. The methodology is used to assess inherent risk, evaluate the effectiveness of controls, and determine residual risk across customers, products, channels, and geographies.",
            "The risk assessment methodology supports the Bank's risk-based approach as required by the PCMLTFA and OSFI Guideline B-8. Results inform the allocation of AML resources and the calibration of monitoring thresholds (MTB-POL-006).",
        ]),
        ("2", "Scope of Risk Assessment", [
            "The methodology applies to the following risk assessment activities:",
            ("bullet", [
                "Enterprise-wide ML/TF risk assessment (annual)",
                "Customer risk scoring (at onboarding and periodically per MTB-POL-002)",
                "Product/service risk assessment (annual or upon new product launch)",
                "Geographic risk assessment (semi-annual)",
                "Channel risk assessment (annual)",
                "Third-party and correspondent banking risk (annual per MTB-POL-005)",
            ]),
        ]),
        ("3", "Risk Assessment Framework", [
        ]),
        ("3.1", "Inherent Risk Assessment", [
            "Inherent risk is the risk of ML/TF before considering the mitigating effect of controls. Inherent risk is assessed across four dimensions:",
            [
                ["Dimension", "Weight", "Risk Factors Considered"],
                ["Customer Risk", "35%", "Customer type, PEP status, sanctions nexus, geographic location, source of wealth"],
                ["Product/Service Risk", "25%", "Cash intensity, anonymity features, international capability, value"],
                ["Channel Risk", "20%", "Non-face-to-face, digital, branch, ATM, third-party"],
                ["Geographic Risk", "20%", "Customer location, transaction destinations, FATF assessments"],
            ],
        ]),
        ("3.2", "Control Effectiveness Assessment", [
            "Controls are assessed for their effectiveness in mitigating inherent risk:",
            [
                ["Control Rating", "Score", "Description"],
                ["Strong", "1", "Controls are well-designed, consistently applied, and regularly tested"],
                ["Adequate", "2", "Controls are designed and generally applied; minor gaps identified"],
                ["Needs Improvement", "3", "Controls exist but have significant gaps; remediation in progress"],
                ["Weak", "4", "Controls are absent or ineffective; immediate remediation required"],
            ],
        ]),
        ("3.3", "Residual Risk Determination", [
            "Residual risk is determined by combining inherent risk and control effectiveness:",
            [
                ["", "Control: Strong", "Control: Adequate", "Control: Needs Improvement", "Control: Weak"],
                ["Inherent: Low", "Low", "Low", "Medium", "High"],
                ["Inherent: Medium-Low", "Low", "Medium-Low", "Medium", "High"],
                ["Inherent: Medium", "Medium-Low", "Medium", "High", "Very High"],
                ["Inherent: High", "Medium", "High", "Very High", "Very High"],
                ["Inherent: Very High", "High", "Very High", "Very High", "Critical"],
            ],
        ]),
        ("4", "Customer Risk Scoring", [
            "Individual customer risk scores (1-100) are calculated using the following weighted factors:",
            [
                ["Factor", "Weight", "Scoring Criteria"],
                ["Customer Type", "20%", "Individual retail (1-2), Commercial (3-5), Wealth (4-6), Institutional (3-7), Cash-intensive business (7-10)"],
                ["Geographic Risk", "20%", "Canada (1-3), US/EU/UK/Australia (3-5), Other low-risk (5-7), Medium-risk (7-8), FATF high-risk (9-10)"],
                ["Product Risk", "15%", "Savings (1-2), Chequing (2-3), Investment (3-5), Credit (3-5), International wire (6-8), Private banking (7-9)"],
                ["Transaction Behaviour", "25%", "Based on 6-month transaction history and anomaly detection (MTB-POL-006)"],
                ["Tenure and Relationship", "10%", "Long-standing (1-3), Medium (4-6), New (7-8), New + high-value (8-10)"],
                ["Source of Funds/Wealth", "10%", "Employment (1-3), Business revenue (3-5), Investment returns (3-5), Unknown (8-10)"],
            ],
            "Customer risk scores are recalculated at each periodic review (MTB-POL-002, Section 5.2) and upon trigger events.",
        ]),
        ("5", "Enterprise Risk Assessment Process", [
            ("bullet", [
                "Step 1: Data collection — gather quantitative and qualitative data on customers, products, channels, geographies",
                "Step 2: Inherent risk rating — rate each risk dimension using the framework in Section 3.1",
                "Step 3: Control mapping — map existing controls to each identified risk",
                "Step 4: Control effectiveness assessment — rate each control per Section 3.2",
                "Step 5: Residual risk determination — apply the matrix in Section 3.3",
                "Step 6: Risk mitigation planning — develop action plans for residual risks rated Medium or above",
                "Step 7: Reporting — present results to Risk Committee and Board",
                "Step 8: Monitoring — track risk indicators and control improvements throughout the year",
            ]),
        ]),
        ("6", "Risk Appetite", [
            "The Board of Directors has approved the following ML/TF risk appetite statement:",
            "\"Maple Trust Bank has no appetite for being used as a vehicle for money laundering or terrorist financing. The Bank accepts that residual ML/TF risk cannot be eliminated entirely but maintains controls to keep residual risk within Low to Medium-Low levels across all business lines.\"",
            "Any residual risk rated Medium or above requires a documented remediation plan approved by the Risk Committee.",
        ]),
        ("7", "Reporting and Governance", [
            [
                ["Report", "Audience", "Frequency"],
                ["Enterprise ML/TF Risk Assessment", "Board of Directors / Risk Committee", "Annually"],
                ["Customer Risk Score Distribution", "CAMLO / Risk Management", "Quarterly"],
                ["Product Risk Assessment", "Risk Committee", "Annually (or upon new product)"],
                ["Control Effectiveness Summary", "Risk Committee / Internal Audit", "Semi-annually"],
                ["Key Risk Indicators (KRI) Dashboard", "CAMLO / Risk Management", "Monthly"],
            ],
        ]),
    ]

    # Build all 10 policies
    # ---- Standard appendix sections added to all policies ----
    def make_standard_appendices(doc_id, title, next_sec_num):
        """Generate standard appendix sections that are added to every policy."""
        n = next_sec_num
        appendices = []

        appendices.append((str(n), "Compliance and Enforcement", [
            f"All Maple Trust Bank employees, contractors, and agents are required to comply with this policy ({doc_id}: {title}). Non-compliance may result in disciplinary action, up to and including termination of employment or contractual relationship.",
            "The Bank is committed to fostering a culture of compliance. Employees who identify potential violations of this policy should report them through the following channels:",
            ("bullet", [
                "Direct supervisor or department manager",
                "Chief Anti-Money Laundering Officer (CAMLO)",
                "Chief Compliance Officer (CCO)",
                "Anonymous Ethics Hotline (1-800-555-0199)",
                "Compliance reporting portal on the Bank's intranet",
            ]),
            "Retaliation against employees who report potential violations in good faith is strictly prohibited under the Bank's Whistleblower Protection Policy and applicable employment legislation.",
            "The AML Compliance team will investigate all reported potential violations and recommend appropriate corrective actions. Investigations will be conducted in accordance with the Bank's internal investigation procedures and applicable privacy legislation (PIPEDA).",
            "The following enforcement actions may be taken depending on the severity and nature of the non-compliance:",
            [
                ["Severity Level", "Examples", "Potential Actions"],
                ["Minor", "Incomplete documentation; late filing of internal forms", "Coaching, additional training, documented warning"],
                ["Moderate", "Failure to complete required KYC refresh; missed periodic review deadline", "Written warning, mandatory retraining, performance impact"],
                ["Serious", "Failure to file STR when warranted; tipping off customer", "Suspension, termination, regulatory reporting"],
                ["Critical", "Deliberate facilitation of ML/TF; destruction of records", "Immediate termination, law enforcement referral, regulatory reporting"],
            ],
        ]))

        appendices.append((str(n+1), "Regulatory References", [
            "This policy has been developed in alignment with the following regulatory instruments, guidelines, and industry standards:",
            [
                ["Reference", "Full Title", "Applicability"],
                ["PCMLTFA", "Proceeds of Crime (Money Laundering) and Terrorist Financing Act, S.C. 2000, c. 17", "Primary Canadian AML/ATF legislation"],
                ["PCMLTFA Regulations", "Proceeds of Crime (Money Laundering) and Terrorist Financing Regulations, SOR/2002-184", "Detailed regulatory requirements"],
                ["OSFI B-8", "OSFI Guideline B-8: Deterring and Detecting Money Laundering and Terrorist Financing", "Supervisory expectations for federally regulated financial institutions"],
                ["FINTRAC Guidance", "FINTRAC Guidance on Reporting, Record-Keeping, Client Identification, and Compliance Programs", "Operational guidance from Canada's financial intelligence unit"],
                ["Criminal Code", "Criminal Code of Canada, Part XII.2 — Proceeds of Crime", "Criminal offences related to money laundering"],
                ["UN Act", "United Nations Act, R.S.C., 1985, c. U-2", "Implementation of UN Security Council sanctions"],
                ["SEMA", "Special Economic Measures Act, S.C. 1992, c. 17", "Canadian autonomous sanctions authority"],
                ["FATF Recommendations", "FATF International Standards on Combating Money Laundering and the Financing of Terrorism & Proliferation", "International AML/CFT standards"],
                ["PIPEDA", "Personal Information Protection and Electronic Documents Act", "Privacy requirements for customer data handling"],
                ["Magnitsky Law", "Justice for Victims of Corrupt Foreign Officials Act, S.C. 2017, c. 21", "Sanctions against foreign corrupt officials"],
            ],
            "This policy is reviewed whenever material amendments to the above regulatory instruments come into effect. The AML Compliance team monitors regulatory developments through subscriptions to OSFI, FINTRAC, and Department of Finance Canada communications.",
            "In the event of conflict between this policy and applicable legislation or regulation, the legislative or regulatory requirement prevails. Any such conflicts identified by Bank personnel must be reported to the CAMLO immediately for resolution.",
        ]))

        appendices.append((str(n+2), "Related Internal Policies and Procedures", [
            "This policy forms part of Maple Trust Bank's comprehensive AML/ATF compliance framework. The following related policies and procedures should be read in conjunction with this document:",
            [
                ["Document ID", "Title", "Relationship"],
                ["MTB-POL-001", "Anti-Money Laundering (AML) Program Policy", "Overarching AML program framework"],
                ["MTB-POL-002", "Know Your Customer (KYC) Procedures", "Customer identification and verification procedures"],
                ["MTB-POL-003", "Suspicious Transaction Reporting Guidelines", "STR filing process and red flag indicators"],
                ["MTB-POL-004", "Customer Due Diligence (CDD) Standards", "Standard and ongoing CDD requirements"],
                ["MTB-POL-005", "Enhanced Due Diligence (EDD) for High-Risk Customers", "Additional due diligence for elevated risk"],
                ["MTB-POL-006", "Transaction Monitoring Program", "Automated and manual transaction surveillance"],
                ["MTB-POL-007", "Sanctions Screening Procedures", "Sanctions list screening and alert handling"],
                ["MTB-POL-008", "Politically Exposed Persons (PEP) Policy", "PEP identification and management"],
                ["MTB-POL-009", "Record Retention and Data Management Policy", "Record-keeping and data lifecycle management"],
                ["MTB-POL-010", "Risk Assessment Methodology", "ML/TF risk scoring and assessment framework"],
            ],
        ]))

        appendices.append((str(n+3), "Policy Review and Update Procedures", [
            "This policy is subject to regular review and update to ensure continued effectiveness and regulatory alignment.",
        ]))
        appendices.append((f"{n+3}.1", "Review Schedule", [
            [
                ["Review Type", "Frequency", "Responsible Party", "Approval"],
                ["Scheduled review", "Annually", "AML Compliance team", "CAMLO"],
                ["Regulatory-triggered review", "Within 90 days of regulatory change", "AML Compliance team", "CAMLO + CCO"],
                ["Incident-triggered review", "Within 30 days of material incident", "AML Compliance + Internal Audit", "Risk Committee"],
                ["Effectiveness review", "Biennially", "External reviewer (as per PCMLTFA)", "Board of Directors"],
            ],
            "All reviews must be documented, including the scope of review, findings, and any recommended changes. Review documentation is retained per MTB-POL-009.",
        ]))
        appendices.append((f"{n+3}.2", "Change Management", [
            "Changes to this policy follow the Bank's policy change management process:",
            ("bullet", [
                "Minor changes (formatting, clarification without substance change): CAMLO approval",
                "Moderate changes (process updates, threshold adjustments): CAMLO + CCO approval",
                "Major changes (new requirements, structural changes): Risk Committee approval",
                "Fundamental changes (complete policy revision): Board of Directors approval",
            ]),
            "All changes must be communicated to affected stakeholders within 30 days of approval. Training materials must be updated within 60 days. The policy version number must be incremented and the version history table updated.",
        ]))

        appendices.append((str(n+4), "Key Contacts", [
            [
                ["Role", "Name", "Department", "Contact"],
                ["Chief Anti-Money Laundering Officer", "Margaret Thompson", "AML Compliance", "m.thompson@mapletrust.ca"],
                ["Chief Compliance Officer", "Sarah Chen", "Enterprise Compliance", "s.chen@mapletrust.ca"],
                ["Chief Risk Officer", "Robert MacLeod", "Enterprise Risk Management", "r.macleod@mapletrust.ca"],
                ["Head of AML Operations", "Priya Sharma", "AML Operations", "p.sharma@mapletrust.ca"],
                ["SVP, Legal & Regulatory", "Jean-Pierre Tremblay", "Legal", "jp.tremblay@mapletrust.ca"],
                ["Director, Internal Audit", "David Kim", "Internal Audit", "d.kim@mapletrust.ca"],
                ["AML Training Coordinator", "Lisa Fontaine", "AML Compliance", "l.fontaine@mapletrust.ca"],
                ["Ethics Hotline", "N/A", "Enterprise Compliance", "1-800-555-0199"],
            ],
        ]))

        appendices.append((str(n+5), "Definitions and Abbreviations", [
            [
                ["Abbreviation", "Full Term"],
                ["AML", "Anti-Money Laundering"],
                ["ATF", "Anti-Terrorist Financing"],
                ["AUM", "Assets Under Management"],
                ["BO", "Beneficial Owner / Beneficial Ownership"],
                ["CAMLO", "Chief Anti-Money Laundering Officer"],
                ["CCO", "Chief Compliance Officer"],
                ["CDD", "Customer Due Diligence"],
                ["CIP", "Customer Identification Program"],
                ["CRO", "Chief Risk Officer"],
                ["EDD", "Enhanced Due Diligence"],
                ["EFT", "Electronic Funds Transfer"],
                ["EFTR", "Electronic Funds Transfer Report"],
                ["EVP", "Executive Vice President"],
                ["FATF", "Financial Action Task Force"],
                ["FINTRAC", "Financial Transactions and Reports Analysis Centre of Canada"],
                ["HIO", "Head of International Organization"],
                ["IEFTR", "International Electronic Funds Transfer Report"],
                ["KRI", "Key Risk Indicator"],
                ["KYC", "Know Your Customer"],
                ["LCTR", "Large Cash Transaction Report"],
                ["ML", "Money Laundering"],
                ["OSFI", "Office of the Superintendent of Financial Institutions"],
                ["PCMLTFA", "Proceeds of Crime (Money Laundering) and Terrorist Financing Act"],
                ["PEP", "Politically Exposed Person"],
                ["PIPEDA", "Personal Information Protection and Electronic Documents Act"],
                ["RBA", "Risk-Based Approach"],
                ["SARF", "Suspicious Activity Referral Form"],
                ["SDN", "Specially Designated Nationals"],
                ["SEMA", "Special Economic Measures Act"],
                ["SIN", "Social Insurance Number"],
                ["SLA", "Service Level Agreement"],
                ["STR", "Suspicious Transaction Report"],
                ["SVP", "Senior Vice President"],
                ["TF", "Terrorist Financing"],
            ],
        ]))

        return appendices

    # Additional content sections for specific policies to reach page targets

    # Add more content to POL-001 (target: 18-20 pages)
    policy_001_extra = [
        ("11.1", "Case Studies and Examples", [
            "The following case studies illustrate common money laundering scenarios that Maple Trust Bank employees should be aware of. These examples are based on FINTRAC typologies and are provided for training and awareness purposes.",
        ]),
        ("11.1.1", "Case Study 1: Structuring Through Multiple Branches", [
            "A customer opens accounts at three different Maple Trust Bank branches within a two-week period. Over the following month, the customer makes cash deposits of between $8,000 and $9,500 at each branch, keeping individual transactions below the $10,000 LCTR threshold. The total monthly cash deposits across all branches exceed $75,000.",
            "Red flags identified: Multiple accounts at different branches; cash deposits consistently below reporting threshold; no apparent business reason for cash-intensive activity; total monthly activity inconsistent with customer's declared occupation (school teacher).",
            "Required actions: Branch staff should have identified the pattern during the second week. Transaction monitoring scenario TM-003 (MTB-POL-006) should generate an automated alert. A SARF should be completed and submitted to the branch Compliance Officer. Given the strong indicators of structuring, an STR filing is likely warranted per MTB-POL-003.",
        ]),
        ("11.1.2", "Case Study 2: Layering Through International Wires", [
            "A recently onboarded commercial customer receives a series of large international wire transfers from multiple countries over a three-month period. The customer then initiates wire transfers of similar amounts to different jurisdictions within 48 hours of receipt. The beneficiary entities in the outgoing wires have no apparent connection to the customer's declared business.",
            "Red flags identified: Rapid movement of funds (in-and-out pattern); international wires to/from multiple jurisdictions; beneficiaries unrelated to declared business; customer is relatively new (limited transaction history for profiling).",
            "Required actions: Transaction monitoring scenarios TM-005, TM-006, and TM-007 (MTB-POL-006) should generate alerts. Enhanced due diligence review per MTB-POL-005 should be initiated. The KYC file should be refreshed to verify the source of incoming funds and the purpose of outgoing transfers. If the customer cannot provide satisfactory explanations, an STR should be filed per MTB-POL-003.",
        ]),
        ("11.1.3", "Case Study 3: Trade-Based Money Laundering", [
            "A commercial customer in the import/export business consistently over-invoices goods imported from a high-risk jurisdiction. The customer pays the inflated invoices through the Bank's wire transfer services. Investigation reveals that the declared value of goods significantly exceeds the fair market value, suggesting potential trade-based money laundering.",
            "Red flags identified: Over-invoicing of goods; transactions with high-risk jurisdiction; invoice amounts inconsistent with industry norms; customer resists providing supporting trade documentation.",
            "Required actions: Enhanced monitoring of all trade-related transactions. Request and review supporting documentation (invoices, bills of lading, customs declarations). Engage the Bank's trade finance compliance team. Consider filing an STR per MTB-POL-003 if suspicious activity is confirmed.",
        ]),
        ("12", "International Operations and Correspondent Banking", [
            "Maple Trust Bank's AML obligations extend to its international operations and correspondent banking relationships. The Bank applies Canadian AML standards as a minimum across all jurisdictions in which it operates.",
        ]),
        ("12.1", "Correspondent Banking Relationships", [
            "Before establishing a correspondent banking relationship, the Bank conducts comprehensive due diligence on the respondent institution, including:",
            ("bullet", [
                "Assessment of the respondent's AML/ATF program and regulatory environment",
                "Review of the respondent's regulatory history and any enforcement actions",
                "Evaluation of the respondent's customer base and geographic risk profile",
                "Confirmation that the respondent is not a shell bank",
                "Senior management approval of the relationship",
                "Annual review and re-assessment of the relationship",
            ]),
            "Nested correspondent banking relationships (payable-through accounts) are subject to additional scrutiny and require CAMLO approval.",
        ]),
        ("12.2", "Cross-Border Considerations", [
            "When Maple Trust Bank operates across borders, it must comply with both Canadian AML requirements and the local AML requirements of the host jurisdiction. Where requirements conflict, the more stringent requirement applies, provided it does not violate local law.",
            "The Bank maintains a register of all jurisdictions in which it operates, along with a comparative analysis of local AML requirements versus Canadian standards. This register is updated annually by the AML Compliance team.",
            [
                ["Jurisdiction", "Local Regulator", "AML Standard Assessment", "Key Differences from Canadian Requirements"],
                ["Canada (Home)", "FINTRAC / OSFI", "Baseline", "N/A"],
                ["United States", "FinCEN / OCC", "Equivalent or higher", "BSA/AML requirements; OFAC sanctions"],
                ["United Kingdom", "FCA", "Equivalent", "MLR 2017; FCA guidance differs on some CDD aspects"],
                ["Cayman Islands", "CIMA", "Lower in some areas", "Enhanced oversight required per OSFI expectations"],
            ],
        ]),
        ("13", "Technology and Innovation", [
            "Maple Trust Bank recognizes the importance of leveraging technology to enhance the effectiveness of its AML program while managing the emerging ML/TF risks associated with new financial technologies.",
        ]),
        ("13.1", "AML Technology Stack", [
            "The Bank's AML technology infrastructure includes the following key systems:",
            [
                ["System", "Vendor/Type", "Function", "Integration"],
                ["Transaction Monitoring", "Rule-based + ML engine", "Automated detection of suspicious patterns", "Real-time feed from core banking"],
                ["Sanctions Screening", "Commercial vendor", "Real-time screening against sanctions lists", "Integrated with wire transfer system"],
                ["Case Management", "Internal system", "Alert investigation and STR workflow", "Fed by monitoring and screening systems"],
                ["Customer Risk Scoring", "ML model (internal)", "Dynamic risk score calculation", "Integrated with CRM and core banking"],
                ["Name Screening", "Commercial vendor", "PEP and adverse media screening", "Batch and real-time modes"],
                ["Regulatory Reporting", "Internal system", "Automated LCTR and EFTR generation", "Direct submission to FINTRAC via F2R"],
            ],
            "The AML technology strategy is reviewed annually as part of the Bank's enterprise technology planning process. New technologies are evaluated for their potential to improve detection effectiveness, reduce false positives, and enhance operational efficiency.",
        ]),
        ("13.2", "Emerging Risk: Digital Assets and Cryptocurrency", [
            "Maple Trust Bank monitors developments in digital assets, cryptocurrency, and decentralized finance (DeFi) as potential sources of ML/TF risk. The Bank does not currently offer cryptocurrency services directly but recognizes that its customers may engage in digital asset transactions through third-party platforms.",
            "The following controls are in place to manage digital asset-related ML/TF risk:",
            ("bullet", [
                "Enhanced monitoring of transactions with known cryptocurrency exchanges",
                "CDD procedures for customers identified as operating cryptocurrency-related businesses",
                "Staff training on digital asset red flags and typologies",
                "Monitoring of regulatory developments regarding virtual asset service providers (VASPs)",
                "Engagement with FINTRAC on emerging virtual currency guidance",
            ]),
        ]),
        ("14", "Whistleblower and Internal Reporting", [
            "The Bank maintains multiple channels for employees to report suspected AML/ATF policy violations or potential money laundering activities. The Bank's Whistleblower Protection Policy ensures that employees who report in good faith are protected from retaliation.",
            "Reports may be made through the following channels:",
            ("bullet", [
                "Direct reporting to the CAMLO or CCO",
                "Anonymous Ethics Hotline: 1-800-555-0199 (operated by independent third party)",
                "Online reporting portal accessible through the Bank's intranet",
                "Written reports submitted to the Internal Audit department",
            ]),
            "All reports are reviewed by the CAMLO or CCO within 5 business days. Substantive reports trigger a formal investigation. The identity of the reporting employee is protected throughout the investigation process.",
            "The Bank is prohibited from taking any retaliatory action against an employee who makes a report in good faith, regardless of the outcome of the investigation.",
        ]),
        ("15", "AML Program Budget and Resource Allocation", [
            "The Board of Directors allocates sufficient resources to the AML program to ensure its effectiveness. The AML program budget is reviewed annually as part of the Bank's overall budget cycle.",
            [
                ["Resource Category", "FY2024 Allocation", "FY2025 Budget", "Change"],
                ["AML Compliance Staff (FTEs)", "45", "52", "+15.6%"],
                ["Transaction Monitoring Technology", "$2.8M", "$3.2M", "+14.3%"],
                ["Sanctions Screening Systems", "$1.1M", "$1.2M", "+9.1%"],
                ["Training and Development", "$450K", "$520K", "+15.6%"],
                ["Third-Party Services (due diligence, screening vendors)", "$1.5M", "$1.7M", "+13.3%"],
                ["Regulatory Reporting Systems", "$600K", "$650K", "+8.3%"],
                ["External Effectiveness Review (biennial)", "$0", "$350K", "Biennial"],
            ],
            "Resource allocation decisions consider the Bank's ML/TF risk profile, regulatory expectations, peer benchmarking, and program effectiveness metrics. Any material budget shortfalls that could impact program effectiveness are reported to the Risk Committee and Board.",
        ]),
        ("16", "Board and Senior Management Oversight", [
            "The Board of Directors is ultimately responsible for the AML program. The following governance structures ensure effective oversight:",
        ]),
        ("16.1", "Board Responsibilities", [
            ("bullet", [
                "Annual approval of the AML program policy and risk appetite statement",
                "Review of the annual enterprise ML/TF risk assessment (MTB-POL-010)",
                "Appointment and oversight of the CAMLO",
                "Review of significant regulatory findings and enforcement actions",
                "Approval of AML program budget and resource allocation",
                "Review of the biennial effectiveness review results",
            ]),
        ]),
        ("16.2", "Risk Committee Responsibilities", [
            ("bullet", [
                "Quarterly review of AML program performance metrics and KRIs",
                "Review and approval of changes to monitoring scenarios and thresholds",
                "Oversight of remediation plans for identified control deficiencies",
                "Review of significant STR filings and trends",
                "Approval of high-risk customer relationship decisions (as escalated by CAMLO)",
            ]),
        ]),
        ("16.3", "Management Reporting Framework", [
            [
                ["Report", "Prepared By", "Audience", "Frequency", "Content"],
                ["CAMLO Quarterly Report", "AML Compliance", "Risk Committee", "Quarterly", "Program performance, alert volumes, STR trends, regulatory updates"],
                ["AML Dashboard", "AML Operations", "CAMLO, CCO", "Monthly", "KRIs, alert metrics, case aging, staffing"],
                ["Enterprise Risk Assessment", "AML Compliance + Risk Mgmt", "Board of Directors", "Annually", "Inherent risk, control effectiveness, residual risk, action plans"],
                ["Effectiveness Review", "External Reviewer", "Board of Directors", "Biennially", "Independent assessment of AML program effectiveness per PCMLTFA"],
                ["Regulatory Exam Summary", "CAMLO", "Risk Committee, Board", "As needed", "Summary of OSFI/FINTRAC examination findings and remediation plans"],
            ],
        ]),
        ("17", "External Examinations and Audits", [
            "Maple Trust Bank is subject to regular examination by external regulators and auditors regarding its AML program. The following table outlines the key external review activities:",
            [
                ["Review Body", "Review Type", "Frequency", "Scope"],
                ["OSFI", "Supervisory examination", "Risk-based (typically every 2-3 years)", "All aspects of AML program; policies, controls, testing"],
                ["FINTRAC", "Compliance examination", "Risk-based", "Reporting obligations, record-keeping, compliance program"],
                ["External Auditor", "AML program effectiveness review", "Biennially (per PCMLTFA s. 9.6)", "Independent assessment of program effectiveness"],
                ["Internal Audit", "AML controls testing", "Annually", "Design and operating effectiveness of AML controls"],
            ],
            "The CAMLO is responsible for coordinating all external examination activities and ensuring timely provision of requested documentation. Examination findings are tracked in the Bank's issues management system with defined remediation timelines and accountable owners.",
            "Any material examination findings must be reported to the Risk Committee within 10 business days. Remediation plans must be developed within 30 days and approved by the Risk Committee. Progress against remediation plans is reported monthly until closure.",
            "The Bank maintains a comprehensive AML examination readiness program that includes:",
            ("bullet", [
                "Continuous maintenance of an AML evidence library with key program documents",
                "Quarterly self-assessment against OSFI B-8 expectations",
                "Pre-examination preparation sessions with all relevant business units",
                "Post-examination lessons learned reviews and process improvements",
                "Tracking of industry examination trends and common findings",
            ]),
        ]),
    ]
    policy_001_sections.extend(policy_001_extra)
    policy_001_sections.extend(make_standard_appendices("MTB-POL-001", "AML Program Policy", 18))

    # Add more content to POL-002 (target: 12-15 pages)
    policy_002_extra = [
        ("10", "Digital and Remote KYC", [
            "With the increasing adoption of digital banking channels, Maple Trust Bank has implemented robust digital KYC procedures that maintain the integrity of customer identification while providing a seamless customer experience.",
        ]),
        ("10.1", "Digital Identity Verification Technologies", [
            "The Bank uses the following approved digital identity verification methods:",
            [
                ["Technology", "Use Case", "Confidence Level", "Limitations"],
                ["Automated document verification", "Photo ID scanning and authentication", "High", "Requires clear image; some foreign IDs not supported"],
                ["Biometric verification", "Facial recognition comparison to ID photo", "High", "Requires customer consent; accessibility considerations"],
                ["Credit bureau verification", "Identity confirmation via credit file match", "Medium-High", "Requires existing credit history; not available for newcomers"],
                ["Digital ID services", "Government digital identity (where available)", "Very High", "Limited availability across provinces"],
                ["Knowledge-based authentication", "Questions based on credit/public records", "Medium", "Susceptible to social engineering; supplementary only"],
            ],
            "For digital channel onboarding, a minimum of two independent verification methods must be used. The results of all digital verification steps must be recorded in the customer's KYC file.",
        ]),
        ("10.2", "Video Verification Procedures", [
            "Video verification calls may be used as an alternative to in-person verification for customers who cannot attend a branch. The following requirements apply:",
            ("bullet", [
                "Video calls must be conducted by trained KYC verification officers",
                "The customer must present their government-issued photo ID during the call",
                "The verification officer must confirm the ID matches the person on the call",
                "The call must be recorded and retained per MTB-POL-009",
                "A screenshot of the ID presented during the call must be captured and stored",
                "Video verification is not available for Very High risk customers (risk score >= 86)",
            ]),
        ]),
        ("11", "Special Categories of Customers", [
        ]),
        ("11.1", "Non-Resident Customers", [
            "Non-resident customers (those residing outside Canada) are subject to additional KYC requirements due to the increased difficulty of verification and ongoing monitoring:",
            ("bullet", [
                "Dual identification is mandatory regardless of risk level",
                "Purpose of the Canadian banking relationship must be clearly documented",
                "Source of funds for account opening must be verified",
                "Tax residency status must be determined for CRS/FATCA reporting",
                "Enhanced monitoring for the first 12 months of the relationship",
                "Risk score baseline is increased by 15 points for non-resident status",
            ]),
        ]),
        ("11.2", "Newcomers to Canada", [
            "Maple Trust Bank recognizes that newcomers to Canada may have limited documentation. The following accommodations are available while maintaining compliance:",
            ("bullet", [
                "Acceptance of valid foreign passport as primary identification",
                "Immigration documents (work permit, study permit, PR card) as supporting ID",
                "Introductory letter from a recognized settlement agency",
                "Phased account opening with transaction limits until full verification is completed",
                "60-day grace period to provide Canadian address verification",
            ]),
            "All accommodations must be documented in the KYC file, and full verification must be completed within 90 days of account opening.",
        ]),
        ("11.3", "Minors and Student Accounts", [
            "For customers under 18 years of age, the following KYC procedures apply:",
            ("bullet", [
                "Parent or legal guardian must be identified and verified using standard CDD",
                "Minor's identity verified through birth certificate or passport",
                "Guardian's risk assessment extends to the minor's account",
                "Transaction limits apply until the customer reaches age of majority",
                "Full individual KYC must be completed within 90 days of the customer turning 18",
            ]),
        ]),
        ("12", "KYC Quality Assurance Program", [
            "The Bank maintains a KYC Quality Assurance (QA) program to ensure consistent application of KYC procedures across all branches and channels.",
        ]),
        ("12.1", "QA Testing Methodology", [
            [
                ["QA Activity", "Sample Size", "Frequency", "Performed By"],
                ["New account KYC file review", "5% of new accounts per branch per month", "Monthly", "Branch Compliance Officer"],
                ["KYC refresh completeness check", "10% of due refreshes", "Quarterly", "AML Compliance team"],
                ["Digital onboarding verification review", "3% of digital accounts", "Monthly", "Digital Compliance team"],
                ["EDD file completeness review", "100% of new EDD files", "Ongoing", "Senior Compliance Officer"],
                ["Cross-branch consistency testing", "25 files per region", "Semi-annually", "Internal Audit"],
            ],
        ]),
        ("12.2", "QA Findings and Remediation", [
            "QA findings are classified by severity and tracked to resolution:",
            ("bullet", [
                "Critical findings: Must be remediated within 5 business days; reported to CAMLO",
                "High findings: Must be remediated within 15 business days; reported to Compliance Officer",
                "Medium findings: Must be remediated within 30 business days; tracked in QA system",
                "Low findings: Must be remediated within 60 business days; included in quarterly reporting",
            ]),
            "Systemic findings (recurring issues across multiple branches or channels) trigger a root cause analysis and potential policy or procedure update. Systemic findings are reported to the Risk Committee.",
        ]),
    ]
    policy_002_sections.extend(policy_002_extra)
    policy_002_sections.extend(make_standard_appendices("MTB-POL-002", "KYC Procedures", 13))

    # Add more content to POL-003 (target: 10-12 pages)
    policy_003_extra = [
        ("9", "STR Writing Standards", [
            "High-quality STR narratives are essential for FINTRAC's analysis. All STR narratives must include the following elements:",
            ("bullet", [
                "Clear description of the suspicious activity or transactions",
                "Why the activity is considered unusual or suspicious (the 'reasonable grounds')",
                "Relevant customer background and profile information",
                "Transaction details including amounts, dates, counterparties, and methods",
                "Any connections to prior alerts, SARFs, or previously filed STRs",
                "Actions taken by the Bank in response to the suspicious activity",
            ]),
            "The STR narrative should be written in clear, factual language without speculation. The narrative should allow a FINTRAC analyst unfamiliar with the case to understand the nature and context of the suspicious activity.",
        ]),
        ("9.1", "Common STR Deficiencies to Avoid", [
            [
                ["Deficiency", "Impact", "Correct Approach"],
                ["Vague narrative", "FINTRAC cannot assess the suspicion", "Provide specific facts, amounts, dates, and context"],
                ["Missing transaction details", "Incomplete picture of the activity", "Include all relevant transactions, not just the triggering one"],
                ["No customer context", "Cannot assess if activity is truly unusual", "Describe the customer's profile, history, and expected behaviour"],
                ["Delayed filing", "Regulatory non-compliance; penalty risk", "File within 30 calendar days of determination"],
                ["Over-reliance on system alerts", "Does not explain human assessment of suspicion", "Document the analyst's own assessment and reasoning"],
            ],
        ]),
        ("10", "Confidentiality and Information Sharing", [
            "The confidentiality of STR-related information is paramount. The following rules govern information sharing:",
        ]),
        ("10.1", "Internal Information Sharing", [
            "STR information may be shared internally on a strict need-to-know basis:",
            ("bullet", [
                "AML analysts investigating the case",
                "Compliance Officers reviewing the STR for quality and completeness",
                "CAMLO for final approval and filing",
                "Legal department when legal advice is required",
                "Internal Audit during authorized compliance testing",
                "Senior management only when necessary for relationship decisions",
            ]),
            "STR information must not be shared with front-line staff who do not have a direct need to know, even if they were involved in the initial detection. Customer-facing staff should be informed only that a 'compliance review' is underway, without disclosing STR details.",
        ]),
        ("10.2", "External Information Sharing", [
            "The Bank may share STR-related information externally only in the following circumstances:",
            ("bullet", [
                "Filing the STR with FINTRAC through the F2R system",
                "Responding to a lawful FINTRAC inquiry or voluntary information request (VIR)",
                "Responding to a court order or lawful production order",
                "Sharing with law enforcement pursuant to a lawful request",
                "Sharing with a foreign affiliate where permitted under PCMLTFA s. 65.1",
            ]),
            "In all cases, the CAMLO and Legal department must approve any external disclosure of STR-related information.",
        ]),
        ("11", "Record Keeping for STRs", [
            "All STR-related records must be retained for a minimum of 5 years from the date of filing, in accordance with MTB-POL-009. This includes:",
            ("bullet", [
                "The STR filing itself (FINTRAC acknowledgment receipt)",
                "All supporting transaction records and analysis",
                "Internal SARF documentation",
                "Investigation notes and case management records",
                "Correspondence with FINTRAC (if any)",
                "Any related alerts from the transaction monitoring system (MTB-POL-006)",
            ]),
            "STR records are classified as 'Restricted' under the Bank's data classification framework (MTB-POL-009, Section 4.1) and are accessible only to authorized AML Compliance personnel.",
        ]),
    ]
    policy_003_sections.extend(policy_003_extra)
    policy_003_sections.extend(make_standard_appendices("MTB-POL-003", "STR Guidelines", 12))

    # Add more to POL-004 (target: 14-16 pages)
    policy_004_extra = [
        ("10", "CDD for Correspondent Banking", [
            "Correspondent banking relationships require enhanced CDD due to the inherent risks of processing transactions on behalf of another financial institution's customers.",
            ("bullet", [
                "Assessment of the respondent institution's AML program adequacy",
                "Review of the respondent's regulatory history and jurisdictional risk",
                "Confirmation that the respondent is not a shell bank or respondent for shell banks",
                "Understanding of the respondent's customer base and transaction types",
                "Annual on-site or desktop review of the respondent's AML controls",
                "Documentation of the correspondent relationship in a formal agreement",
            ]),
            "The Bank does not establish correspondent banking relationships with shell banks, or with institutions that permit their accounts to be used by shell banks. Payable-through accounts are prohibited without explicit CAMLO approval.",
        ]),
        ("11", "CDD for Trusts and Legal Arrangements", [
            "Trusts and other legal arrangements present unique CDD challenges due to the separation of legal and beneficial ownership. The following information must be obtained:",
            [
                ["Trust Role", "Information Required", "Verification"],
                ["Settlor", "Full name, DOB, address, occupation", "Government-issued photo ID"],
                ["Trustee(s)", "Full name, DOB, address, professional qualifications", "Government-issued photo ID; professional registration"],
                ["Beneficiaries (named)", "Full name, DOB, address", "Government-issued photo ID"],
                ["Beneficiaries (class)", "Description of the class of beneficiaries", "Trust deed review"],
                ["Protector (if any)", "Full name, DOB, address, powers held", "Government-issued photo ID; trust deed"],
            ],
            "All parties to the trust must be screened against sanctions lists (MTB-POL-007) and PEP databases (MTB-POL-008). The trust deed or equivalent document must be reviewed by the Compliance team.",
        ]),
        ("12", "CDD for Non-Profit Organizations", [
            "Non-profit organizations (NPOs) may present elevated ML/TF risk due to the nature of their funding sources and disbursements. Additional CDD measures include:",
            ("bullet", [
                "Review of the NPO's charitable registration with the Canada Revenue Agency",
                "Understanding of the NPO's sources of funding (donations, grants, fundraising)",
                "Assessment of the geographic areas in which the NPO operates",
                "Review of the NPO's governance structure and key personnel",
                "Verification that the NPO is not associated with any listed terrorist organization",
                "Enhanced monitoring of international disbursements, particularly to high-risk jurisdictions",
            ]),
        ]),
        ("13", "CDD in Mergers and Acquisitions", [
            "When Maple Trust Bank acquires another financial institution or merges with one, CDD obligations extend to the acquired customer base. The following procedures apply:",
            ("bullet", [
                "Pre-acquisition assessment of the target's AML program and customer risk profile",
                "Risk-based prioritization of customer file reviews (highest risk first)",
                "All high-risk and very high-risk customers must have CDD refreshed within 90 days",
                "Medium-risk customers must have CDD refreshed within 180 days",
                "Low-risk customers must have CDD refreshed within 12 months",
                "Any deficiencies in the acquired institution's CDD documentation must be remediated",
            ]),
        ]),
        ("14", "CDD Performance Metrics", [
            "The Bank tracks the following metrics to monitor CDD program effectiveness:",
            [
                ["Metric", "Target", "Reporting"],
                ["New account CDD completion rate", ">= 98% within SLA", "Monthly"],
                ["KYC refresh on-time rate", ">= 90%", "Monthly"],
                ["CDD deficiency rate (QA findings)", "< 5%", "Quarterly"],
                ["Average time to complete CDD for new customers", "< 5 business days (standard)", "Monthly"],
                ["EDD completion rate within SLA", ">= 95%", "Monthly"],
                ["Beneficial ownership identification rate (corporate)", "100%", "Quarterly"],
            ],
        ]),
        ("15", "CDD Exceptions and Exemptions", [
            "Certain categories of customers may be eligible for simplified CDD under specific circumstances, as permitted by the PCMLTFA. These exceptions are narrowly defined and must be documented:",
            [
                ["Category", "Simplified CDD Permitted", "Conditions"],
                ["Listed public companies", "Yes", "Listed on a recognized Canadian exchange; annual filings current"],
                ["Regulated financial institutions", "Yes", "Subject to PCMLTFA or equivalent foreign AML regulation"],
                ["Government entities", "Yes", "Federal, provincial, or municipal government bodies"],
                ["Crown corporations", "Yes", "Established by Canadian federal or provincial legislation"],
                ["Registered pension funds", "Yes", "Registered under the Pension Benefits Standards Act or provincial equivalent"],
            ],
            "Simplified CDD does not exempt these customers from sanctions screening (MTB-POL-007) or PEP screening (MTB-POL-008). Any simplified CDD decision must be reviewed by the Compliance Officer and documented in the customer file.",
        ]),
        ("16", "CDD Technology and Automation", [
            "Maple Trust Bank utilizes technology to support CDD processes while maintaining human oversight for risk decisions:",
            ("bullet", [
                "Automated identity verification services for government-issued ID authentication",
                "Credit bureau integration for address and identity confirmation",
                "Automated beneficial ownership lookups through corporate registry services",
                "Digital document collection and storage through secure customer portal",
                "Workflow automation for CDD review scheduling and task assignment",
                "Automated risk scoring integration with CDD review triggers",
                "AI-assisted name matching for adverse media and sanctions screening",
            ]),
            "All automated CDD decisions are subject to human review. Technology-assisted CDD does not reduce the Bank's obligations under the PCMLTFA — it enhances the efficiency and consistency of CDD processes.",
        ]),
    ]
    policy_004_sections.extend(policy_004_extra)
    policy_004_sections.extend(make_standard_appendices("MTB-POL-004", "CDD Standards", 17))

    # Add more to POL-005 (target: 8-10 pages)
    policy_005_extra = [
        ("7", "EDD Case Studies", [
        ]),
        ("7.1", "Case Study: High-Risk Jurisdiction", [
            "A wealth management client requests the opening of an investment account. The client is a citizen and resident of a FATF-identified high-risk jurisdiction. The client has significant wealth from real estate investments in their home country.",
            "EDD measures applied: Full source of wealth documentation including property records and business financial statements; independent verification through third-party background check; enhanced media screening in multiple languages; CAMLO approval with SVP Risk endorsement; quarterly review frequency; enhanced transaction monitoring at 50% of standard thresholds.",
        ]),
        ("7.2", "Case Study: Complex Corporate Ownership", [
            "A corporate customer applies for commercial banking services. The ownership structure involves a holding company registered in the Cayman Islands, which in turn is owned by a trust established in the Channel Islands. The ultimate beneficial owners are two individuals who are citizens of an EU country.",
            "EDD measures applied: Full ownership chain documentation with verification at each layer; identification and verification of both ultimate beneficial owners; review of trust deed and holding company incorporation documents; independent legal opinion on the ownership structure; Senior Compliance Officer and CAMLO approval; semi-annual review with annual on-site relationship review.",
        ]),
        ("8", "EDD Monitoring and Reporting", [
            [
                ["Metric", "Target", "Reporting Frequency"],
                ["EDD portfolio size (number of customers)", "Tracked", "Monthly"],
                ["EDD completion rate within SLA", ">= 95%", "Monthly"],
                ["EDD periodic review on-time rate", ">= 90%", "Quarterly"],
                ["EDD-related STR rate", "Tracked (no target)", "Quarterly"],
                ["EDD exit rate", "Tracked (no target)", "Quarterly"],
                ["Average time from EDD trigger to completion", "< 30 business days", "Monthly"],
            ],
            "The CAMLO reports on the EDD portfolio to the Risk Committee on a quarterly basis, including trends in the size and composition of the EDD customer base, key risk themes, and any material findings.",
        ]),
        ("9", "EDD Staff Competency Requirements", [
            "Staff involved in EDD activities must meet the following competency requirements:",
            ("bullet", [
                "Minimum 3 years of experience in AML compliance or financial crime investigation",
                "Completion of the Bank's Advanced AML Training program",
                "Familiarity with PCMLTFA requirements, OSFI B-8, and FINTRAC guidance",
                "Understanding of complex corporate structures, trusts, and legal arrangements",
                "Proficiency in source of wealth and source of funds analysis",
                "Annual recertification through the Bank's AML competency assessment",
            ]),
        ]),
    ]
    policy_005_sections.extend(policy_005_extra)
    policy_005_sections.extend(make_standard_appendices("MTB-POL-005", "EDD Policy", 10))

    # Add more to POL-006 (target: 15-18 pages)
    policy_006_extra = [
        ("9", "Tuning and Optimization", [
            "The transaction monitoring system requires ongoing tuning and optimization to maintain effectiveness while managing alert volumes. The following tuning activities are performed:",
        ]),
        ("9.1", "Threshold Review Process", [
            "Monitoring thresholds are reviewed semi-annually using the following methodology:",
            ("bullet", [
                "Above-the-line analysis: Review all STRs filed in the period; confirm that the monitoring system generated alerts for the underlying activity",
                "Below-the-line analysis: Sample transactions below alert thresholds to identify potential missed suspicious activity",
                "Peer benchmarking: Compare threshold levels with industry standards and regulatory expectations",
                "Statistical analysis: Review alert volume, disposition rates, and STR conversion rates by scenario",
                "Regulatory feedback: Incorporate any FINTRAC or OSFI feedback on the monitoring program",
            ]),
        ]),
        ("9.2", "Model Performance Metrics", [
            [
                ["Metric", "Formula", "Target", "Action if Below Target"],
                ["Precision", "True Positives / (True Positives + False Positives)", ">= 10%", "Review scenario rules and thresholds"],
                ["Recall", "True Positives / (True Positives + False Negatives)", ">= 95%", "Expand scenario coverage; lower thresholds"],
                ["F1 Score", "2 * (Precision * Recall) / (Precision + Recall)", ">= 0.18", "Comprehensive model review"],
                ["AUC-ROC (ML models)", "Area under ROC curve", ">= 0.75", "Model retraining or replacement"],
                ["Alert-to-SAR ratio", "SARs filed / Total alerts investigated", ">= 5%", "Review alert generation logic"],
            ],
        ]),
        ("10", "Scenario Development and Retirement", [
        ]),
        ("10.1", "New Scenario Development", [
            "New monitoring scenarios are developed in response to:",
            ("bullet", [
                "FINTRAC typology reports and operational alerts",
                "FATF mutual evaluation findings and recommendations",
                "Internal case studies and emerging patterns identified by AML analysts",
                "Regulatory feedback or examination findings from OSFI",
                "Industry intelligence shared through the Canadian AML community",
                "New products or services launched by the Bank",
            ]),
            "New scenario development follows the Bank's change management process. Each new scenario requires documentation of the rationale, rule logic, expected alert volumes, and a calibration period of at least 90 days before production deployment.",
        ]),
        ("10.2", "Scenario Retirement", [
            "Scenarios may be retired if they are no longer effective or relevant. Retirement requires:",
            ("bullet", [
                "Documented analysis demonstrating that the scenario is no longer effective (e.g., zero STR conversions over 12 months)",
                "Confirmation that the ML/TF risk addressed by the scenario is covered by other scenarios or controls",
                "CAMLO approval for scenario retirement",
                "Documentation retained for regulatory review purposes",
            ]),
        ]),
        ("11", "Batch and Real-Time Processing", [
            "The transaction monitoring system operates in both batch and real-time modes to provide comprehensive coverage:",
            [
                ["Processing Mode", "Scope", "Schedule", "Alert Delivery"],
                ["Real-time", "Sanctions screening; high-priority wire transfers", "Continuous", "Immediate — blocks transaction pending review"],
                ["Near real-time", "Large cash transactions; EFT threshold detection", "Every 15 minutes", "Alert queue within 30 minutes"],
                ["Daily batch", "All rule-based scenarios; ML anomaly scoring", "Nightly (2:00 AM ET)", "Alert queue by 7:00 AM ET"],
                ["Weekly batch", "Network analysis; relationship pattern detection", "Sunday (midnight ET)", "Alert queue by Monday 7:00 AM ET"],
                ["Monthly batch", "Customer behaviour profiling; peer group analysis", "1st of each month", "Alert queue within 24 hours"],
            ],
        ]),
        ("12", "Data Requirements for Transaction Monitoring", [
            "The transaction monitoring system requires complete and accurate data from multiple source systems. The following data feeds are critical:",
            [
                ["Data Feed", "Source System", "Frequency", "Key Fields", "Quality SLA"],
                ["Customer transactions", "Core banking", "Daily", "Account, amount, date, type, counterparty", "99.5% completeness"],
                ["Wire transfers", "SWIFT gateway", "Real-time", "Sender, receiver, amount, currency, country", "99.9% completeness"],
                ["Customer profile", "CRM", "Daily", "Name, DOB, occupation, risk score, segment", "99.0% completeness"],
                ["Account data", "Core banking", "Daily", "Account type, status, balance, branch", "99.5% completeness"],
                ["KYC status", "KYC platform", "Daily", "Verification status, expiry, risk level", "99.0% completeness"],
                ["Sanctions lists", "Vendor feed", "Daily", "Name, aliases, DOB, country, list source", "100% completeness"],
            ],
            "Data quality issues that impact transaction monitoring effectiveness are escalated to the Data Governance team and tracked through the Bank's data quality management framework. Persistent data quality issues are reported to the CAMLO and may be escalated to the Risk Committee.",
        ]),
        ("13", "Transaction Monitoring for Specific Products", [
        ]),
        ("13.1", "Mortgage and Lending Monitoring", [
            "Mortgage and lending products are monitored for the following ML/TF scenarios:",
            ("bullet", [
                "Rapid prepayment of mortgage or loan (potential integration of proceeds of crime)",
                "Third-party payments on behalf of the borrower",
                "Property purchases significantly above or below market value",
                "Multiple mortgage applications across branches within a short period",
                "Use of mortgage proceeds inconsistent with stated purpose",
            ]),
        ]),
        ("13.2", "Investment Account Monitoring", [
            "Investment accounts are monitored for:",
            ("bullet", [
                "Unusual trading patterns (e.g., purchase and rapid liquidation of securities)",
                "Large cash deposits to investment accounts",
                "Transfers between investment accounts without apparent investment purpose",
                "Requests to transfer securities to third-party accounts",
                "Significant changes in investment behaviour inconsistent with customer profile",
            ]),
        ]),
        ("13.3", "Credit Card Monitoring", [
            "Credit card activity is monitored for:",
            ("bullet", [
                "Overpayment of credit card balance followed by cash advance or balance transfer",
                "Use of credit card for purchases inconsistent with customer profile",
                "Frequent large payments to the credit card from third-party sources",
                "Credit card use in high-risk jurisdictions inconsistent with travel patterns",
            ]),
        ]),
        ("14", "Staffing and Organization", [
            "The AML Transaction Monitoring team is organized as follows:",
            [
                ["Role", "Count", "Primary Responsibility", "Reporting Line"],
                ["Director, Transaction Monitoring", "1", "Overall program management and strategy", "CAMLO"],
                ["Senior AML Analysts", "8", "Complex case investigation; STR preparation", "Director, TM"],
                ["AML Analysts", "15", "Alert investigation and disposition", "Senior AML Analysts"],
                ["Junior AML Analysts", "10", "Initial alert triage and data gathering", "AML Analysts"],
                ["Model Development Analysts", "4", "ML model development and validation", "Director, TM"],
                ["Data Engineers", "3", "Data pipeline maintenance and monitoring", "Director, TM"],
                ["QA Specialist", "2", "Alert disposition quality review", "Director, TM"],
            ],
            "Staffing levels are reviewed semi-annually against alert volumes and disposition time SLAs. If alert backlogs exceed 5 business days on a sustained basis, temporary staffing augmentation is authorized by the CAMLO.",
        ]),
        ("15", "Incident Response for Monitoring System Failures", [
            "In the event of a transaction monitoring system outage or degradation, the following procedures apply:",
            ("bullet", [
                "Immediate notification to the CAMLO and IT Operations",
                "Activation of manual monitoring procedures for high-priority scenarios (TM-001 through TM-005)",
                "IT to prioritize system restoration per the Bank's incident management framework",
                "Upon system restoration, backfill processing of all transactions during the outage period",
                "Post-incident review to identify root cause and preventive measures",
                "If outage exceeds 24 hours, notification to OSFI as a significant operational incident",
                "Documentation of all manual monitoring activities during the outage",
            ]),
            "The Bank maintains a documented Business Continuity Plan (BCP) for the transaction monitoring function, which is tested annually. The BCP includes manual monitoring procedures, escalation protocols, and recovery priorities.",
        ]),
    ]
    policy_006_sections.extend(policy_006_extra)
    policy_006_sections.extend(make_standard_appendices("MTB-POL-006", "Transaction Monitoring", 16))

    # Add more to POL-007 (target: 8-10 pages)
    policy_007_extra = [
        ("8", "Sanctions Compliance Training", [
            "All employees involved in transaction processing, customer onboarding, or compliance functions must complete sanctions compliance training:",
            [
                ["Role", "Training Content", "Frequency"],
                ["Front-line staff", "Basic sanctions awareness; red flags; escalation procedures", "Annually"],
                ["Wire transfer operations", "Detailed sanctions screening; hold procedures; alert handling", "Semi-annually"],
                ["Compliance analysts", "Advanced sanctions analysis; list interpretation; disposition", "Quarterly"],
                ["Senior management", "Sanctions program governance; regulatory obligations; risk oversight", "Annually"],
            ],
        ]),
        ("9", "Sanctions Regime Updates", [
            "The Bank's sanctions compliance program must respond promptly to sanctions regime changes:",
            ("bullet", [
                "Canadian sanctions list updates: Screen within 24 hours of publication",
                "US OFAC updates: Screen within 24 hours for USD transaction exposure",
                "UN Security Council updates: Screen within 24 hours of resolution",
                "EU updates: Screen within 48 hours for EUR transaction exposure",
                "Emergency designations: Immediate screening upon notification",
            ]),
            "The Compliance team subscribes to automated notifications from Global Affairs Canada, OFAC, and the UN Security Council Committee. List updates are loaded into the screening system and tested before activation.",
        ]),
        ("10", "Sanctions Risk Assessment", [
            "The Bank conducts an annual sanctions risk assessment that evaluates:",
            ("bullet", [
                "Customer base exposure to sanctioned jurisdictions",
                "Product and service exposure (particularly international wire transfers)",
                "Geographic risk based on branch locations and customer distribution",
                "Third-party relationships that may introduce sanctions exposure",
                "Effectiveness of screening systems and processes",
                "Regulatory expectations and industry best practices",
            ]),
            "Results of the sanctions risk assessment are reported to the Risk Committee and inform the calibration of screening thresholds and alert handling procedures.",
        ]),
        ("11", "Record Keeping for Sanctions Screening", [
            "All sanctions screening records must be retained for 5 years per MTB-POL-009, including:",
            ("bullet", [
                "Screening results for all customers (positive and negative matches)",
                "Alert investigation documentation and disposition rationale",
                "True match escalation records and regulatory filings",
                "List update logs and system configuration changes",
                "Training records for sanctions-related training",
            ]),
        ]),
    ]
    policy_007_sections.extend(policy_007_extra)
    policy_007_sections.extend(make_standard_appendices("MTB-POL-007", "Sanctions Screening", 12))

    # Add more to POL-008 (target: 6-8 pages)
    policy_008_extra = [
        ("7", "PEP Monitoring and Review", [
            "PEP relationships are subject to enhanced ongoing monitoring:",
            ("bullet", [
                "All transactions reviewed against expected activity profile",
                "Quarterly compliance review of the PEP file by designated Compliance Officer",
                "Annual comprehensive review including source of wealth update",
                "Continuous adverse media monitoring through automated screening",
                "Real-time transaction monitoring at enhanced thresholds (MTB-POL-006)",
            ]),
        ]),
        ("8", "PEP Risk Assessment Integration", [
            "PEP status is a significant factor in the customer risk assessment (MTB-POL-010). The following risk score adjustments apply:",
            [
                ["PEP Category", "Base Risk Score Adjustment", "Minimum Risk Classification"],
                ["Domestic PEP — Municipal", "+15 points", "Medium"],
                ["Domestic PEP — Provincial", "+20 points", "Medium"],
                ["Domestic PEP — Federal", "+25 points", "High"],
                ["Foreign PEP — Low-risk country", "+25 points", "High"],
                ["Foreign PEP — Medium-risk country", "+35 points", "High"],
                ["Foreign PEP — High-risk country", "+45 points", "Very High"],
                ["Head of International Organization", "+30 points", "High"],
                ["PEP Family Member", "Same as associated PEP", "Same as associated PEP"],
                ["Close Associate", "Associated PEP adjustment minus 5 points", "One level below associated PEP"],
            ],
        ]),
    ]
    policy_008_sections.extend(policy_008_extra)
    policy_008_sections.extend(make_standard_appendices("MTB-POL-008", "PEP Policy", 9))

    # Add more to POL-009 (target: 10-12 pages)
    policy_009_extra = [
        ("8", "Data Governance Framework", [
            "Record retention and data management operate within Maple Trust Bank's broader data governance framework. The following governance structures and processes apply:",
        ]),
        ("8.1", "Data Governance Roles", [
            [
                ["Role", "Responsibility", "Accountability"],
                ["Chief Data Officer (CDO)", "Enterprise data strategy and governance oversight", "Data governance program effectiveness"],
                ["Data Stewards", "Domain-specific data quality and standards management", "Data quality within assigned domains"],
                ["Data Custodians", "Technical management of data storage and access controls", "System availability and data security"],
                ["Data Owners", "Business accountability for data assets in their domain", "Data classification and access decisions"],
                ["Privacy Officer", "PIPEDA compliance and privacy impact assessments", "Privacy compliance across all data domains"],
            ],
        ]),
        ("8.2", "Data Architecture Standards", [
            "The Bank's data architecture follows a three-layer model aligned with industry best practices:",
            [
                ["Layer", "Purpose", "Data Characteristics", "Retention"],
                ["Raw / Landing", "Ingestion of data from source systems", "Unmodified source data; full fidelity", "Per source system SLA (minimum 90 days)"],
                ["Curated / Conformed", "Cleaned, validated, and standardized data", "Deduplicated; schema-enforced; master data linked", "Per business domain requirements"],
                ["Consumed / Presentation", "Analytics, reporting, and application data", "Aggregated; enriched; business-ready", "Per reporting and regulatory requirements"],
            ],
            "Data lineage is tracked across all three layers. The Bank maintains a data lineage graph that documents the flow of data from source systems through transformations to consuming applications. This supports regulatory compliance, impact analysis, and data quality management.",
        ]),
        ("9", "Regulatory Response Procedures", [
            "The Bank must be able to respond to regulatory data requests within defined timeframes:",
            [
                ["Request Source", "Response Timeframe", "Approval Required", "Process"],
                ["FINTRAC production order", "Within the timeframe specified in the order", "Legal + CAMLO", "Legal reviews order; coordinates data retrieval"],
                ["FINTRAC voluntary information request", "30 calendar days", "CAMLO", "CAMLO reviews and coordinates response"],
                ["OSFI examination data request", "As specified by OSFI", "CCO + CRO", "Compliance coordinates data retrieval"],
                ["Law enforcement production order", "Per court order terms", "Legal + CAMLO", "Legal reviews order; coordinates with law enforcement"],
                ["Customer access request (PIPEDA)", "30 calendar days", "Privacy Officer", "Privacy team processes request"],
            ],
        ]),
        ("10", "Disaster Recovery for AML Records", [
            "AML-related records are classified as critical data assets and are subject to the Bank's disaster recovery requirements:",
            ("bullet", [
                "Recovery Point Objective (RPO): 4 hours maximum for active AML records",
                "Recovery Time Objective (RTO): 8 hours for AML systems and records",
                "Geographic redundancy: AML records replicated to secondary data centre",
                "Annual DR testing: AML record recovery tested as part of annual DR exercise",
                "Backup encryption: All backup media encrypted using AES-256",
                "Backup validation: Monthly restore testing of a sample of AML records",
            ]),
        ]),
        ("11", "Legal Hold Procedures", [
            "When a legal hold is issued, normal retention and destruction schedules are suspended for the affected records. Legal holds may be issued in response to:",
            ("bullet", [
                "Litigation or anticipated litigation involving the Bank",
                "Regulatory investigation or enforcement action",
                "Internal investigation into potential misconduct",
                "Law enforcement request to preserve records",
            ]),
            "The Legal department is responsible for issuing and managing legal holds. All employees who receive a legal hold notice must immediately suspend any destruction of the affected records and acknowledge receipt of the notice.",
            "Legal holds remain in effect until formally released by the Legal department. Records subject to a legal hold must not be destroyed even if their normal retention period has expired.",
        ]),
    ]
    policy_009_sections.extend(policy_009_extra)
    policy_009_sections.extend(make_standard_appendices("MTB-POL-009", "Record Retention", 12))

    # Add more to POL-010 (target: 12-14 pages)
    policy_010_extra = [
        ("8", "Quantitative Risk Indicators", [
            "The Bank tracks the following quantitative Key Risk Indicators (KRIs) to support ongoing risk assessment:",
            [
                ["KRI", "Metric", "Threshold (Amber)", "Threshold (Red)", "Reporting"],
                ["High-risk customer ratio", "% of customer base rated High or Very High", "> 8%", "> 12%", "Monthly"],
                ["STR filing volume", "Number of STRs filed per quarter", "< 10 or > 100", "< 5 or > 150", "Quarterly"],
                ["Alert-to-SAR ratio", "% of investigated alerts resulting in STR", "< 3%", "< 1%", "Monthly"],
                ["KYC overdue rate", "% of KYC reviews past due", "> 10%", "> 20%", "Monthly"],
                ["Cash transaction ratio", "Cash transactions as % of total (by value)", "> 15%", "> 25%", "Monthly"],
                ["International wire concentration", "% of wires to/from high-risk jurisdictions", "> 5%", "> 10%", "Monthly"],
                ["New high-risk customer volume", "Number of new high-risk customers per month", "> 50", "> 100", "Monthly"],
                ["EDD portfolio growth", "Month-over-month EDD portfolio growth", "> 10%", "> 20%", "Monthly"],
            ],
            "KRI breaches at the Amber level require investigation and documentation by the AML Compliance team. KRI breaches at the Red level require immediate escalation to the CAMLO and reporting to the Risk Committee.",
        ]),
        ("9", "Scenario Analysis and Stress Testing", [
            "The Bank conducts scenario analysis and stress testing to assess the resilience of its AML controls under adverse conditions:",
            ("bullet", [
                "Scenario 1: Significant increase in cash transaction volumes (e.g., due to natural disaster or economic crisis)",
                "Scenario 2: Rapid growth in high-risk customer segments (e.g., due to acquisition)",
                "Scenario 3: Technology failure affecting transaction monitoring for an extended period",
                "Scenario 4: Regulatory changes requiring immediate program modifications",
                "Scenario 5: Discovery of systematic control failure in a business line or branch",
            ]),
            "Scenario analysis is conducted annually as part of the enterprise risk assessment. Results are reported to the Risk Committee and inform the development of contingency plans for each scenario.",
        ]),
        ("10", "Peer and Industry Benchmarking", [
            "The Bank benchmarks its ML/TF risk profile and AML program against industry peers:",
            [
                ["Benchmark Area", "Data Source", "Frequency"],
                ["STR filing volumes", "FINTRAC annual reports", "Annually"],
                ["Alert volumes and disposition rates", "Industry surveys and peer group sharing", "Annually"],
                ["AML program spending (% of revenue)", "Industry surveys", "Annually"],
                ["Technology investment in AML", "Vendor reports and industry surveys", "Annually"],
                ["Regulatory examination findings", "OSFI public enforcement actions", "Ongoing"],
                ["False positive rates", "Industry working groups", "Semi-annually"],
            ],
            "Benchmarking results are incorporated into the annual enterprise risk assessment and used to identify areas where the Bank's AML program may be under- or over-performing relative to peers.",
        ]),
        ("11", "Risk Assessment for New Products and Services", [
            "Before launching any new product, service, or channel, a ML/TF risk assessment must be completed:",
            ("bullet", [
                "Risk assessment must be initiated at the product design stage, not at launch",
                "Assessment must cover customer risk, product risk, channel risk, and geographic risk",
                "AML controls must be designed and tested before product launch",
                "Transaction monitoring scenarios must be developed or adapted for the new product",
                "Post-launch monitoring plan must be in place for the first 12 months",
                "The CAMLO must approve the risk assessment before product launch",
            ]),
            "New product risk assessments are documented using the Bank's standard risk assessment template and retained per MTB-POL-009.",
        ]),
        ("12", "Third-Party Risk Assessment", [
            "Third parties that perform AML-related functions on behalf of the Bank (e.g., outsourced screening, identity verification vendors) are subject to risk assessment:",
            [
                ["Assessment Area", "Evaluation Criteria"],
                ["AML program adequacy", "Does the third party have an AML program commensurate with the services provided?"],
                ["Regulatory compliance", "Is the third party subject to AML regulation in its jurisdiction?"],
                ["Data security", "Does the third party meet the Bank's data security standards?"],
                ["Business continuity", "Does the third party have adequate business continuity arrangements?"],
                ["Concentration risk", "Is the Bank overly dependent on this third party for a critical AML function?"],
                ["Geographic risk", "Is the third party located in or operating from a high-risk jurisdiction?"],
            ],
            "Third-party risk assessments are conducted prior to engagement and reviewed annually. The results inform the overall enterprise ML/TF risk assessment.",
        ]),
    ]
    policy_010_sections.extend(policy_010_extra)
    policy_010_sections.extend(make_standard_appendices("MTB-POL-010", "Risk Assessment", 13))

    all_policies = [
        ("MTB-POL-001.pdf", "MTB-POL-001", "Anti-Money Laundering (AML) Program Policy", "3.1", "2024-01-15", policy_001_sections),
        ("MTB-POL-002.pdf", "MTB-POL-002", "Know Your Customer (KYC) Procedures", "2.4", "2024-02-01", policy_002_sections),
        ("MTB-POL-003.pdf", "MTB-POL-003", "Suspicious Transaction Reporting Guidelines", "2.2", "2024-01-15", policy_003_sections),
        ("MTB-POL-004.pdf", "MTB-POL-004", "Customer Due Diligence (CDD) Standards", "3.0", "2024-03-01", policy_004_sections),
        ("MTB-POL-005.pdf", "MTB-POL-005", "Enhanced Due Diligence (EDD) for High-Risk Customers", "2.1", "2024-03-01", policy_005_sections),
        ("MTB-POL-006.pdf", "MTB-POL-006", "Transaction Monitoring Program", "2.5", "2024-02-15", policy_006_sections),
        ("MTB-POL-007.pdf", "MTB-POL-007", "Sanctions Screening Procedures", "1.8", "2024-04-01", policy_007_sections),
        ("MTB-POL-008.pdf", "MTB-POL-008", "Politically Exposed Persons (PEP) Policy", "2.0", "2024-03-15", policy_008_sections),
        ("MTB-POL-009.pdf", "MTB-POL-009", "Record Retention and Data Management Policy", "2.3", "2024-01-01", policy_009_sections),
        ("MTB-POL-010.pdf", "MTB-POL-010", "Risk Assessment Methodology", "3.2", "2024-01-15", policy_010_sections),
    ]

    for filename, doc_id, title, version, effective_date, sections in all_policies:
        filepath = build_pdf(filename, doc_id, title, version, effective_date, sections)
        print(f"  Generated {filepath}")


# ---------------------------------------------------------------------------
# Eval set generator
# ---------------------------------------------------------------------------

def generate_eval_set(output_dir: Path) -> Path:
    """Generate 30 Q&A pairs against the policy corpus."""
    eval_dir = output_dir / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)
    filepath = eval_dir / "aml_qa_eval.jsonl"

    qa_pairs = [
        # --- Factual lookups (15) ---
        {
            "question": "What is the reporting threshold for large cash transactions under FINTRAC requirements?",
            "answer": "$10,000 CAD or more in cash, as per PCMLTFA and FINTRAC guidelines. Multiple cash transactions within a 24-hour period that total $10,000 CAD or more from the same individual also trigger reporting.",
            "source_doc": "MTB-POL-003.pdf",
            "section": "3.1",
        },
        {
            "question": "What is the filing deadline for a Suspicious Transaction Report (STR)?",
            "answer": "STRs must be filed with FINTRAC within 30 calendar days of the determination that there are reasonable grounds to suspect money laundering or terrorist financing.",
            "source_doc": "MTB-POL-003.pdf",
            "section": "3.2",
        },
        {
            "question": "What is the minimum name matching threshold used in the sanctions screening system?",
            "answer": "The automated sanctions screening system uses a minimum 85% similarity threshold for name matching, with phonetic matching (Soundex and Double Metaphone) also enabled.",
            "source_doc": "MTB-POL-007.pdf",
            "section": "5.1",
        },
        {
            "question": "How long must customer identification records be retained after account closure?",
            "answer": "Customer identification records must be retained for 5 years after account closure or last transaction, stored in a secure digital archive.",
            "source_doc": "MTB-POL-009.pdf",
            "section": "3",
        },
        {
            "question": "What risk score range is classified as 'High' risk requiring Enhanced Due Diligence?",
            "answer": "Customers with a risk score of 71-85 are classified as 'High' risk and require Enhanced Due Diligence (EDD) with semi-annual review. Scores of 86-100 are 'Very High' risk requiring EDD plus Senior Management approval with quarterly review.",
            "source_doc": "MTB-POL-001.pdf",
            "section": "5.2",
        },
        {
            "question": "What percentage ownership triggers beneficial ownership identification requirements?",
            "answer": "Any individual who directly or indirectly owns or controls 25% or more of an entity must be identified as a beneficial owner, as per PCMLTFA requirements.",
            "source_doc": "MTB-POL-004.pdf",
            "section": "5.1",
        },
        {
            "question": "What is the filing deadline for International Electronic Funds Transfer Reports (IEFTRs)?",
            "answer": "International Electronic Funds Transfer Reports must be filed within 5 business days for international EFTs of $10,000 CAD or more.",
            "source_doc": "MTB-POL-003.pdf",
            "section": "3.3",
        },
        {
            "question": "How often must front-line staff (tellers, CSRs) complete AML training?",
            "answer": "Front-line staff including tellers and Customer Service Representatives must complete AML training semi-annually, with content focused on red flags, customer identification, and STR escalation.",
            "source_doc": "MTB-POL-001.pdf",
            "section": "9",
        },
        {
            "question": "What is the response time SLA for Critical priority transaction monitoring alerts?",
            "answer": "Critical priority alerts must be responded to on the same business day. Disposition options include Escalate, Investigate, or File STR.",
            "source_doc": "MTB-POL-006.pdf",
            "section": "5.1",
        },
        {
            "question": "How long does a person remain classified as a domestic PEP after leaving their prescribed position?",
            "answer": "A domestic PEP remains classified for 5 years after leaving the prescribed position, as per PCMLTFA requirements. De-listing requires Compliance Officer approval and documentation.",
            "source_doc": "MTB-POL-008.pdf",
            "section": "5",
        },
        {
            "question": "What secure destruction method is required for physical documents?",
            "answer": "Physical documents must be destroyed using cross-cut shredding at DIN 66399 Level P-4 minimum, with a certificate of destruction issued.",
            "source_doc": "MTB-POL-009.pdf",
            "section": "7",
        },
        {
            "question": "What is the target false positive rate for the transaction monitoring system?",
            "answer": "The target false positive rate for the transaction monitoring system is less than 90%, with reporting on a monthly basis.",
            "source_doc": "MTB-POL-006.pdf",
            "section": "8",
        },
        {
            "question": "What weight does Customer Risk carry in the inherent risk assessment?",
            "answer": "Customer Risk carries a 35% weight in the inherent risk assessment, making it the highest-weighted dimension. Product/Service Risk is 25%, Channel Risk is 20%, and Geographic Risk is 20%.",
            "source_doc": "MTB-POL-010.pdf",
            "section": "3.1",
        },
        {
            "question": "How many lines of defence are defined in the AML governance structure?",
            "answer": "Three lines of defence: First Line (business units and front-line staff), Second Line (AML Compliance and Risk Management), and Third Line (Internal Audit).",
            "source_doc": "MTB-POL-001.pdf",
            "section": "4.2",
        },
        {
            "question": "What is the minimum travel rule threshold for electronic funds transfers?",
            "answer": "Travel rule information must accompany all EFTs of $1,000 CAD or more.",
            "source_doc": "MTB-POL-003.pdf",
            "section": "3.3",
        },
        # --- Multi-document reasoning (10) ---
        {
            "question": "If a customer's risk score increases from 60 to 75, what additional due diligence requirements apply and how does the review cycle change?",
            "answer": "When a customer's risk score crosses from Medium (51-70) to High (71-85), Enhanced Due Diligence (EDD) is triggered per MTB-POL-005. The review frequency changes from annually to semi-annually (MTB-POL-001, Section 5.2). EDD requires additional source of wealth documentation, Senior Compliance Officer approval, and enhanced transaction monitoring at 50% of standard thresholds (MTB-POL-005, Section 4). The KYC file must be refreshed as this constitutes a trigger event (MTB-POL-002, Section 5.1).",
            "source_doc": "MTB-POL-001.pdf,MTB-POL-002.pdf,MTB-POL-005.pdf",
            "section": "5.2,5.1,2",
        },
        {
            "question": "How do the transaction monitoring scenarios in the Transaction Monitoring Program relate to the red flag indicators in the Suspicious Transaction Reporting Guidelines?",
            "answer": "The transaction monitoring scenarios in MTB-POL-006 are designed to automatically detect the red flag indicators described in MTB-POL-003. For example, scenario TM-003 detects structuring (cash transactions of $8,000-$9,999 with 3+ occurrences in 7 days), which corresponds to the 'Structuring' red flag in MTB-POL-003, Section 4.2. Similarly, TM-009 (dormant account reactivation) matches the 'Dormant account activity' red flag. When alerts are generated, they follow the STR filing process outlined in MTB-POL-003, Section 5.",
            "source_doc": "MTB-POL-003.pdf,MTB-POL-006.pdf",
            "section": "4.2,4",
        },
        {
            "question": "What is the complete lifecycle of a sanctions match for a customer identified as both a PEP and a sanctions hit?",
            "answer": "First, sanctions screening (MTB-POL-007) identifies the match. If confirmed as a True Match, assets are frozen immediately, reported to FINTRAC as a Terrorist Property Report, and reported to OSFI. Simultaneously, PEP status (MTB-POL-008) requires EDD per MTB-POL-005 with CAMLO + SVP Risk approval for foreign PEPs. The customer's risk score would be elevated to Very High (86-100) per MTB-POL-010, requiring quarterly reviews. All records must be retained for 5 years per MTB-POL-009. The CAMLO must report to the Board through the Risk Committee per MTB-POL-001, Section 4.1.",
            "source_doc": "MTB-POL-007.pdf,MTB-POL-008.pdf,MTB-POL-005.pdf,MTB-POL-001.pdf",
            "section": "5.2,4,3.2,4.1",
        },
        {
            "question": "How does the risk assessment methodology influence transaction monitoring thresholds?",
            "answer": "The risk assessment methodology (MTB-POL-010) assigns each customer a risk score from 1-100 based on weighted factors including customer type (20%), geographic risk (20%), product risk (15%), transaction behaviour (25%), tenure (10%), and source of funds (10%). This score determines the monitoring intensity in MTB-POL-006: standard thresholds for low/medium risk, and 50% of standard thresholds for EDD customers (MTB-POL-005, Section 4). Monitoring thresholds are calibrated semi-annually based on the risk assessment results.",
            "source_doc": "MTB-POL-010.pdf,MTB-POL-006.pdf,MTB-POL-005.pdf",
            "section": "4,4,4",
        },
        {
            "question": "What records must be retained when exiting a high-risk customer relationship, and for how long?",
            "answer": "Per MTB-POL-005 Section 6, the exit decision must be documented with rationale. Per MTB-POL-009 Section 3, CDD/EDD assessment files must be retained for 5 years after the relationship ends, customer identification records for 5 years after account closure, transaction records for 5 years from transaction date, and any STRs filed for 5 years from filing date. Additionally, the risk assessment records (MTB-POL-010) must be kept for 5 years from assessment date. Consideration must be given to filing a final STR per MTB-POL-003 before exit.",
            "source_doc": "MTB-POL-005.pdf,MTB-POL-009.pdf,MTB-POL-003.pdf",
            "section": "6,3,5",
        },
        {
            "question": "How are non-face-to-face customers treated differently across KYC, CDD, and transaction monitoring?",
            "answer": "Non-face-to-face customers require additional verification measures per MTB-POL-002 Section 7: two-factor authentication, digital ID verification, credit bureau check, and enhanced monitoring for the first 90 days. Non-face-to-face onboarding may not be available for High or Very High risk customers. CDD procedures per MTB-POL-004 still apply fully. The Channel Risk dimension in MTB-POL-010 (weighted at 20%) rates non-face-to-face channels as higher risk, which can elevate the customer's overall score and potentially trigger EDD per MTB-POL-005.",
            "source_doc": "MTB-POL-002.pdf,MTB-POL-004.pdf,MTB-POL-010.pdf",
            "section": "7,3,3.1",
        },
        {
            "question": "What is the connection between the KYC periodic review schedule and the risk assessment methodology?",
            "answer": "The KYC periodic review schedule (MTB-POL-002, Section 5.2) is directly driven by the risk assessment results (MTB-POL-010). Low-risk retail customers are reviewed every 36 months, while high-risk institutional customers are reviewed every 3 months. At each periodic review, the customer's risk score is recalculated using the methodology in MTB-POL-010 Section 4. If the score crosses a threshold boundary, this constitutes a trigger event (MTB-POL-002, Section 5.1) that may change the CDD level from standard (MTB-POL-004) to enhanced (MTB-POL-005).",
            "source_doc": "MTB-POL-002.pdf,MTB-POL-010.pdf,MTB-POL-004.pdf",
            "section": "5.2,4,3",
        },
        {
            "question": "How does the three lines of defence model in the AML policy manifest in the responsibilities defined across the other policy documents?",
            "answer": "The First Line (business units) is reflected in MTB-POL-002 where CSRs collect KYC, MTB-POL-003 where all employees detect and report suspicious activity via SARFs, and MTB-POL-004 where relationship managers perform ongoing CDD. The Second Line (AML Compliance) appears in MTB-POL-006 where AML analysts investigate alerts, MTB-POL-007 where sanctions analysts disposition screening alerts, and MTB-POL-005 where Compliance Officers approve EDD. The Third Line (Internal Audit) is referenced across all policies as performing independent testing of controls.",
            "source_doc": "MTB-POL-001.pdf,MTB-POL-002.pdf,MTB-POL-003.pdf,MTB-POL-006.pdf",
            "section": "4.2,8,8,5.2",
        },
        {
            "question": "What data quality requirements exist across the policy framework, and how do they support effective AML compliance?",
            "answer": "MTB-POL-009 Section 4.2 defines data quality standards: completeness, accuracy, timeliness, consistency, accessibility, and integrity. MTB-POL-006 Section 7 requires transaction data completeness for monitoring effectiveness, current customer profiles per MTB-POL-002 review schedules, documented data lineage, and daily data reconciliation. MTB-POL-002 Section 6 specifies KYC documentation standards including legibility, dating, and electronic retention. Together, these requirements ensure that transaction monitoring (MTB-POL-006), risk scoring (MTB-POL-010), and sanctions screening (MTB-POL-007) operate on reliable data.",
            "source_doc": "MTB-POL-009.pdf,MTB-POL-006.pdf,MTB-POL-002.pdf",
            "section": "4.2,7,6",
        },
        {
            "question": "How does the Bank's risk appetite statement influence the residual risk targets and control requirements across the policy framework?",
            "answer": "The risk appetite statement in MTB-POL-010 Section 6 declares the Bank maintains controls to keep residual risk within Low to Medium-Low levels. This drives control requirements across all policies: MTB-POL-006 sets monitoring SLAs and coverage targets (>= 90% of FINTRAC typologies), MTB-POL-007 requires real-time sanctions screening with 24-hour list updates, MTB-POL-002 mandates periodic KYC reviews at frequencies determined by risk level, and MTB-POL-005 requires senior management approval for high-risk relationships. Any residual risk rated Medium or above requires a documented remediation plan approved by the Risk Committee.",
            "source_doc": "MTB-POL-010.pdf,MTB-POL-006.pdf,MTB-POL-007.pdf",
            "section": "6,8,3",
        },
        # --- Procedural questions (5) ---
        {
            "question": "What steps should a teller follow when a customer makes a cash deposit of $12,000 CAD?",
            "answer": "1) Process the transaction normally. 2) Since the amount exceeds $10,000 CAD, an LCTR is automatically triggered and must be filed with FINTRAC within 15 calendar days (MTB-POL-003, Section 3.1). 3) Assess whether the transaction is consistent with the customer's profile (MTB-POL-004, ongoing CDD). 4) If anything appears suspicious (e.g., customer seems nervous, inconsistent with profile), complete a Suspicious Activity Referral Form (SARF) and submit to the branch Compliance Officer within 24 hours (MTB-POL-003, Section 5.1). 5) Do not inform the customer about any reporting obligations — this would violate tipping-off provisions (MTB-POL-003, Section 6).",
            "source_doc": "MTB-POL-003.pdf",
            "section": "3.1,5.1,6",
        },
        {
            "question": "What is the procedure when a sanctions screening alert identifies a potential match on an outgoing wire transfer?",
            "answer": "1) The wire transfer is held pending resolution (MTB-POL-007, Section 5.2). 2) The potential match must be resolved within 4 business hours for wire transfers. 3) The Sanctions Screening Analyst reviews the alert, comparing customer data against the sanctioned entity details. 4) If confirmed as a True Match: immediately escalate to CAMLO and Legal; freeze assets; file a Terrorist Property Report with FINTRAC immediately; notify OSFI. 5) If False Positive: document the rationale and release the wire. 6) All screening results are retained for 5 years per MTB-POL-009.",
            "source_doc": "MTB-POL-007.pdf",
            "section": "5.2",
        },
        {
            "question": "How should a relationship manager handle a trigger event where a retail customer's occupation changes to a senior government role?",
            "answer": "1) This constitutes a trigger event for KYC refresh (MTB-POL-002, Section 5.1). 2) Screen the customer against PEP databases — the government role may qualify as a domestic PEP (MTB-POL-008, Section 2). 3) If PEP status confirmed, apply EDD requirements per MTB-POL-005: obtain source of wealth, enhanced monitoring, Senior Compliance Officer approval. 4) Update the customer's risk score per MTB-POL-010 methodology — PEP status will increase the score. 5) Adjust the review frequency per MTB-POL-002, Section 5.2 based on the new risk level. 6) Update CDD documentation per MTB-POL-004. 7) Enable enhanced transaction monitoring thresholds per MTB-POL-006.",
            "source_doc": "MTB-POL-002.pdf,MTB-POL-008.pdf,MTB-POL-005.pdf",
            "section": "5.1,3,3",
        },
        {
            "question": "What should an AML analyst do when they receive a High priority transaction monitoring alert?",
            "answer": "Per MTB-POL-006, Section 5: 1) The alert must be responded to within 2 business days. 2) Perform initial triage — review transaction details and customer profile. 3) Investigate — gather supporting information, review prior alerts and SARFs. 4) Assess against red flag indicators in MTB-POL-003, Section 4. 5) Check customer's risk score and CDD/EDD status per MTB-POL-004/MTB-POL-005. 6) Disposition: either close with documented rationale, investigate further, or escalate for STR consideration. 7) If escalating, forward to CAMLO for STR decision per MTB-POL-003, Section 5.2. 8) Complete investigation notes. 9) Alert may be selected for quality review by supervisor.",
            "source_doc": "MTB-POL-006.pdf,MTB-POL-003.pdf",
            "section": "5.1,5.2,5",
        },
        {
            "question": "What is the process for onboarding a new corporate customer with complex multi-layered ownership?",
            "answer": "1) Collect standard corporate CDD documents per MTB-POL-004, Section 2: Certificate of Incorporation, business registration, director details. 2) Identify all beneficial owners at every layer of the ownership structure — the 25% threshold applies at each level (MTB-POL-004, Section 5). 3) Complex ownership triggers EDD per MTB-POL-005 — obtain senior management approval. 4) Verify beneficial ownership through corporate registry searches, shareholder registers, and documentary evidence (MTB-POL-004, Section 5.2). 5) Screen all directors and beneficial owners against sanctions lists (MTB-POL-007) and PEP databases (MTB-POL-008). 6) Assign risk score per MTB-POL-010 — complex ownership will elevate the score. 7) Document everything per MTB-POL-009 standards. 8) Set review frequency based on resulting risk level per MTB-POL-002.",
            "source_doc": "MTB-POL-004.pdf,MTB-POL-005.pdf,MTB-POL-007.pdf,MTB-POL-008.pdf",
            "section": "5,2,3,3",
        },
    ]

    with open(filepath, "w") as f:
        for qa in qa_pairs:
            f.write(json.dumps(qa) + "\n")

    return filepath


# ---------------------------------------------------------------------------
# Lineage graph generator
# ---------------------------------------------------------------------------

def generate_lineage_graph(output_dir: Path) -> Path:
    """Generate a synthetic data lineage graph (JSON)."""
    lineage_dir = output_dir / "lineage"
    lineage_dir.mkdir(parents=True, exist_ok=True)
    filepath = lineage_dir / "lineage_graph.json"

    graph = {
        "nodes": [
            # Raw layer — source system extracts
            {"id": "raw.transactions", "layer": "raw", "source": "core_banking_extract", "format": "csv", "description": "Daily transaction extract from core banking system", "refresh": "daily", "owner": "data_engineering"},
            {"id": "raw.customers", "layer": "raw", "source": "crm_extract", "format": "csv", "description": "Customer master data from CRM system", "refresh": "daily", "owner": "data_engineering"},
            {"id": "raw.accounts", "layer": "raw", "source": "core_banking_extract", "format": "csv", "description": "Account master data from core banking", "refresh": "daily", "owner": "data_engineering"},
            {"id": "raw.branches", "layer": "raw", "source": "branch_management_system", "format": "csv", "description": "Branch reference data", "refresh": "weekly", "owner": "data_engineering"},
            {"id": "raw.kyc_records", "layer": "raw", "source": "kyc_platform_extract", "format": "json", "description": "KYC verification records and status", "refresh": "daily", "owner": "compliance_data"},
            {"id": "raw.sanctions_lists", "layer": "raw", "source": "sanctions_vendor_feed", "format": "xml", "description": "Consolidated sanctions lists from vendor", "refresh": "daily", "owner": "compliance_data"},
            {"id": "raw.wire_transfers", "layer": "raw", "source": "swift_gateway", "format": "csv", "description": "International wire transfer messages", "refresh": "real-time", "owner": "data_engineering"},

            # Curated layer — cleaned and transformed
            {"id": "curated.transactions_clean", "layer": "curated", "source": "spark_etl_job_001", "format": "parquet", "description": "Deduplicated transactions with normalized currencies", "refresh": "daily", "owner": "data_engineering"},
            {"id": "curated.customer_360", "layer": "curated", "source": "mdm_pipeline", "format": "parquet", "description": "Unified customer view with resolved entities", "refresh": "daily", "owner": "mdm_team"},
            {"id": "curated.accounts_enriched", "layer": "curated", "source": "spark_etl_job_002", "format": "parquet", "description": "Accounts enriched with customer and branch data", "refresh": "daily", "owner": "data_engineering"},
            {"id": "curated.kyc_status_current", "layer": "curated", "source": "spark_etl_job_003", "format": "parquet", "description": "Current KYC status with expiry tracking", "refresh": "daily", "owner": "compliance_data"},
            {"id": "curated.wire_transfers_enriched", "layer": "curated", "source": "spark_etl_job_004", "format": "parquet", "description": "Wire transfers enriched with country risk scores", "refresh": "daily", "owner": "data_engineering"},
            {"id": "curated.sanctions_reference", "layer": "curated", "source": "sanctions_etl_pipeline", "format": "parquet", "description": "Normalized sanctions list for screening", "refresh": "daily", "owner": "compliance_data"},

            # Consumed layer — analytics and reporting
            {"id": "consumed.branch_summary_quarterly", "layer": "consumed", "source": "dbt_model_branch_agg", "format": "iceberg", "description": "Quarterly branch performance summary", "refresh": "quarterly", "owner": "analytics_team"},
            {"id": "consumed.aml_alerts", "layer": "consumed", "source": "aml_scoring_pipeline", "format": "parquet", "description": "AML risk alerts from transaction monitoring", "refresh": "daily", "owner": "aml_operations"},
            {"id": "consumed.customer_risk_scores", "layer": "consumed", "source": "risk_scoring_model_v3", "format": "parquet", "description": "Customer ML/TF risk scores", "refresh": "daily", "owner": "aml_operations"},
            {"id": "consumed.regulatory_reports", "layer": "consumed", "source": "reporting_pipeline", "format": "csv", "description": "FINTRAC regulatory report data (LCTRs, STRs, EFTRs)", "refresh": "daily", "owner": "compliance_data"},
            {"id": "consumed.customer_segmentation", "layer": "consumed", "source": "ml_segmentation_model", "format": "parquet", "description": "Customer segmentation for marketing and risk", "refresh": "monthly", "owner": "analytics_team"},
            {"id": "consumed.kyc_dashboard_data", "layer": "consumed", "source": "dbt_model_kyc_metrics", "format": "iceberg", "description": "KYC compliance metrics for dashboard", "refresh": "daily", "owner": "compliance_data"},
        ],
        "edges": [
            # Raw to Curated
            {"from": "raw.transactions", "to": "curated.transactions_clean", "transform": "dedup + schema enforcement + currency normalization to CAD (Bank of Canada daily rates)"},
            {"from": "raw.customers", "to": "curated.customer_360", "transform": "entity resolution + dedup + PII standardization + address normalization"},
            {"from": "raw.accounts", "to": "curated.accounts_enriched", "transform": "join with customer_360 and branches + status derivation + balance validation"},
            {"from": "raw.branches", "to": "curated.accounts_enriched", "transform": "branch reference data lookup for region and manager enrichment"},
            {"from": "raw.kyc_records", "to": "curated.kyc_status_current", "transform": "flatten JSON + compute expiry dates + derive current status"},
            {"from": "raw.sanctions_lists", "to": "curated.sanctions_reference", "transform": "XML parsing + normalization + alias expansion + dedup"},
            {"from": "raw.wire_transfers", "to": "curated.wire_transfers_enriched", "transform": "SWIFT message parsing + country risk scoring + currency conversion"},
            {"from": "raw.customers", "to": "curated.accounts_enriched", "transform": "customer dimension lookup for account enrichment"},

            # Curated to Curated (cross-enrichment)
            {"from": "curated.customer_360", "to": "curated.accounts_enriched", "transform": "customer segment and risk profile join"},
            {"from": "curated.transactions_clean", "to": "curated.wire_transfers_enriched", "transform": "transaction reference matching for wire transfers"},

            # Curated to Consumed
            {"from": "curated.transactions_clean", "to": "consumed.branch_summary_quarterly", "transform": "aggregate by branch + quarter, compute volume/value metrics"},
            {"from": "curated.accounts_enriched", "to": "consumed.branch_summary_quarterly", "transform": "account count and balance aggregation by branch"},
            {"from": "curated.transactions_clean", "to": "consumed.aml_alerts", "transform": "rule-based scenario detection + ML anomaly scoring"},
            {"from": "curated.customer_360", "to": "consumed.aml_alerts", "transform": "customer risk profile enrichment for alert context"},
            {"from": "curated.wire_transfers_enriched", "to": "consumed.aml_alerts", "transform": "high-risk jurisdiction detection + pattern analysis"},
            {"from": "curated.customer_360", "to": "consumed.customer_risk_scores", "transform": "weighted risk factor scoring model (MTB-POL-010 methodology)"},
            {"from": "curated.transactions_clean", "to": "consumed.customer_risk_scores", "transform": "transaction behaviour features (6-month rolling window)"},
            {"from": "curated.kyc_status_current", "to": "consumed.customer_risk_scores", "transform": "KYC status and verification completeness features"},
            {"from": "curated.transactions_clean", "to": "consumed.regulatory_reports", "transform": "filter cash >= $10K CAD for LCTR; flag suspicious for STR review"},
            {"from": "curated.wire_transfers_enriched", "to": "consumed.regulatory_reports", "transform": "filter international EFTs >= $10K CAD for IEFTR generation"},
            {"from": "curated.customer_360", "to": "consumed.customer_segmentation", "transform": "feature engineering + k-means clustering + segment labelling"},
            {"from": "curated.transactions_clean", "to": "consumed.customer_segmentation", "transform": "transaction pattern features for behavioural segmentation"},
            {"from": "curated.kyc_status_current", "to": "consumed.kyc_dashboard_data", "transform": "aggregate KYC metrics by status, segment, branch; compute SLA compliance"},
            {"from": "curated.customer_360", "to": "consumed.kyc_dashboard_data", "transform": "customer segment dimensions for KYC metric drill-down"},
            {"from": "curated.sanctions_reference", "to": "consumed.aml_alerts", "transform": "real-time name/entity matching against normalized sanctions list"},
        ],
        "metadata": {
            "generated_at": "2025-01-15T10:00:00Z",
            "pipeline_version": "2.3.1",
            "bank": "Maple Trust Bank",
            "description": "Data lineage graph showing flow from raw source extracts through curated transformations to consumed analytics and reporting layers.",
            "total_nodes": 19,
            "total_edges": 25,
        },
    }

    with open(filepath, "w") as f:
        json.dump(graph, f, indent=2)

    return filepath


# ---------------------------------------------------------------------------
# MDM entity links generator
# ---------------------------------------------------------------------------

def generate_entity_links(
    customers_df: pd.DataFrame,
    seed: int = 42,
    n_entities: int = 200,
    n_rows: int = 500,
) -> pd.DataFrame:
    """Generate ~500 MDM entity link records."""
    rng = np.random.default_rng(seed)
    py_rng = random.Random(seed)

    source_systems = ["core_banking", "crm", "aml_system", "branch_records"]
    match_methods = ["exact_name_dob", "fuzzy_name_address", "ssn_match", "manual_review"]
    match_method_weights = [0.40, 0.30, 0.15, 0.15]

    customer_ids = customers_df["customer_id"].values

    # Select n_entities unique customers to serve as resolved entities
    selected_customers = rng.choice(customer_ids, size=n_entities, replace=False)

    rows = []
    entity_idx = 0
    row_count = 0

    for cust_id in selected_customers:
        entity_idx += 1
        entity_id = f"ENT-{entity_idx:04d}"

        # Each entity has 2-4 source system records
        n_records = rng.choice([2, 3, 4], p=[0.40, 0.40, 0.20])
        systems = rng.choice(source_systems, size=n_records, replace=False)

        for sys in systems:
            # Generate a source_id that looks like it came from that system
            if sys == "core_banking":
                source_id = f"CB-{rng.integers(100000, 999999)}"
            elif sys == "crm":
                source_id = f"CRM-{rng.integers(100000, 999999)}"
            elif sys == "aml_system":
                source_id = f"AML-{rng.integers(10000, 99999)}"
            else:
                source_id = f"BR-{rng.integers(10000, 99999)}"

            method = rng.choice(match_methods, p=match_method_weights)
            # Confidence depends on method
            if method == "exact_name_dob":
                confidence = round(rng.uniform(0.95, 1.0), 3)
            elif method == "ssn_match":
                confidence = round(rng.uniform(0.98, 1.0), 3)
            elif method == "fuzzy_name_address":
                confidence = round(rng.uniform(0.70, 0.95), 3)
            else:  # manual_review
                confidence = round(rng.uniform(0.80, 0.99), 3)

            last_updated = datetime.datetime(2024, 1, 1) + datetime.timedelta(
                days=int(rng.integers(0, 365)),
                hours=int(rng.integers(8, 18)),
                minutes=int(rng.integers(0, 60)),
            )

            rows.append({
                "entity_id": entity_id,
                "source_system": sys,
                "source_id": source_id,
                "customer_id": cust_id,
                "match_confidence": confidence,
                "match_method": method,
                "last_updated": last_updated,
            })
            row_count += 1

            if row_count >= n_rows:
                break
        if row_count >= n_rows:
            break

    df = pd.DataFrame(rows)
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic BFSI dataset for Maple Trust Bank."
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--output-dir", type=Path, default=DATA_DIR,
        help="Output directory for generated files",
    )
    args = parser.parse_args()

    seed = args.seed
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating synthetic dataset (seed={seed}) in {output_dir}")
    print("=" * 60)

    # 1. Branches
    print("\n[1/8] Generating branches (50 rows)...")
    branches_df = generate_branches(seed)
    branches_df.to_parquet(output_dir / "branches.parquet", index=False)
    print(f"  Saved {len(branches_df)} branches to branches.parquet")

    # 2. Customers
    print("\n[2/8] Generating customers (100K rows)...")
    customers_df = generate_customers(seed)
    customers_df.to_parquet(output_dir / "customers.parquet", index=False)
    print(f"  Saved {len(customers_df)} customers to customers.parquet")

    # 3. Accounts
    print("\n[3/8] Generating accounts (200K rows)...")
    accounts_df = generate_accounts(customers_df, branches_df, seed)
    accounts_df.to_parquet(output_dir / "accounts.parquet", index=False)
    print(f"  Saved {len(accounts_df)} accounts to accounts.parquet")

    # 4. Transactions
    print("\n[4/8] Generating transactions (1M rows)...")
    transactions_df = generate_transactions(accounts_df, customers_df, seed)
    transactions_df.to_parquet(output_dir / "transactions.parquet", index=False)
    print(f"  Saved {len(transactions_df)} transactions to transactions.parquet")

    # 5. Policy PDFs
    print("\n[5/8] Generating policy PDFs (10 documents)...")
    generate_policies(output_dir, seed)
    print("  All policy PDFs generated.")

    # 6. Eval set
    print("\n[6/8] Generating eval set (30 Q&A pairs)...")
    eval_path = generate_eval_set(output_dir)
    print(f"  Saved eval set to {eval_path}")

    # 7. Lineage graph
    print("\n[7/8] Generating lineage graph...")
    lineage_path = generate_lineage_graph(output_dir)
    print(f"  Saved lineage graph to {lineage_path}")

    # 8. MDM entity links
    print("\n[8/8] Generating MDM entity links (500 rows)...")
    entity_links_df = generate_entity_links(customers_df, seed)
    entity_links_df.to_parquet(output_dir / "mdm" / "entity_links.parquet", index=False)
    print(f"  Saved {len(entity_links_df)} entity links to mdm/entity_links.parquet")

    print("\n" + "=" * 60)
    print("Dataset generation complete!")
    print(f"\nOutput directory: {output_dir}")
    print("\nGenerated files:")
    for f in sorted(output_dir.rglob("*")):
        if f.is_file():
            size = f.stat().st_size
            if size > 1_000_000:
                size_str = f"{size / 1_000_000:.1f} MB"
            elif size > 1_000:
                size_str = f"{size / 1_000:.1f} KB"
            else:
                size_str = f"{size} B"
            print(f"  {f.relative_to(output_dir)} ({size_str})")


if __name__ == "__main__":
    main()
