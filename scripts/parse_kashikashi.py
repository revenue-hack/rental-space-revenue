#!/usr/bin/env python3
"""Normalize a Kashikashi settlement CSV or PDF to auditable JSON."""

import argparse
import csv
import json
import re
from pathlib import Path


ALIASES = {
    "date": ["日付", "利用日"],
    "reservation_id": ["予約ID", "予約id"],
    "space": ["スペース名", "施設名"],
    "sale": ["売上", "売上金額"],
    "fee": ["手数料", "成約手数料"],
    "payout": ["支払金額", "受取額"],
}


def yen(value):
    if value is None or str(value).strip() == "":
        return None
    cleaned = re.sub(r"[^0-9-]", "", str(value))
    return int(cleaned) if cleaned not in ("", "-") else None


def pick(headers, names):
    normalized = {re.sub(r"\s+", "", h).lower(): h for h in headers}
    for name in names:
        hit = normalized.get(re.sub(r"\s+", "", name).lower())
        if hit:
            return hit
    return None


def parse_csv(path):
    raw = path.read_bytes()
    text = None
    for encoding in ("utf-8-sig", "cp932", "utf-8"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        raise ValueError("CSV encoding is not UTF-8 or CP932")
    dialect = csv.Sniffer().sniff(text[:4096], delimiters=",\t;")
    rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    if not rows:
        raise ValueError("CSV has no data rows")
    fields = {key: pick(rows[0].keys(), aliases) for key, aliases in ALIASES.items()}
    missing = [key for key in ("reservation_id", "date", "space", "sale") if not fields[key]]
    if missing:
        raise ValueError(f"Required CSV columns not found: {', '.join(missing)}")
    bookings = []
    for row in rows:
        rid = str(row.get(fields["reservation_id"], "")).strip()
        if not rid:
            continue
        bookings.append({
            "reservation_id": rid,
            "date": row.get(fields["date"], "").strip(),
            "space": row.get(fields["space"], "").strip(),
            "sale": yen(row.get(fields["sale"])),
            "fee": yen(row.get(fields["fee"])) if fields["fee"] else None,
            "payout": yen(row.get(fields["payout"])) if fields["payout"] else None,
        })
    return {"platform": "カシカシ", "bookings": bookings, "transfer_fee": None, "scheduled_payout": None, "warnings": []}


def pdf_text(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required to read PDF statements") from exc
    return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)


def parse_pdf(path):
    text = pdf_text(path)
    payout_match = re.search(r"支払予定金額\s*[￥¥]?\s*([0-9,]+)", text)
    transfer_match = re.search(r"振込手数料\s*[￥¥]?\s*([0-9,]+)", text)
    row_re = re.compile(
        r"(?:^|\n)\s*\d+\s+(\d{4}年\d{1,2}月\d{1,2}日)\s+(\d{6,})\s+(.+?)\s+利用料\s+[￥¥]?([0-9,]+)\s+[￥¥]?([0-9,]+)\s+[￥¥]?([0-9,]+)",
        re.MULTILINE,
    )
    bookings = [
        {"date": m.group(1), "reservation_id": m.group(2), "space": m.group(3).strip(),
         "sale": yen(m.group(4)), "fee": yen(m.group(5)), "payout": yen(m.group(6))}
        for m in row_re.finditer(text)
    ]
    warnings = []
    if not bookings:
        warnings.append("No booking rows parsed; inspect the PDF layout or OCR quality")
    scheduled = yen(payout_match.group(1)) if payout_match else None
    transfer = yen(transfer_match.group(1)) if transfer_match else None
    if bookings and scheduled is not None and transfer is not None:
        calculated = sum(x["payout"] or 0 for x in bookings) - transfer
        if calculated != scheduled:
            warnings.append(f"Payout mismatch: calculated {calculated}, statement {scheduled}")
    return {"platform": "カシカシ", "bookings": bookings, "transfer_fee": transfer, "scheduled_payout": scheduled, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.source.suffix.lower() == ".pdf":
        result = parse_pdf(args.source)
    elif args.source.suffix.lower() in (".csv", ".tsv"):
        result = parse_csv(args.source)
    else:
        raise SystemExit("Supported formats: PDF, CSV, TSV")
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
