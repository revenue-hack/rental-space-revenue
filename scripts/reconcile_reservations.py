#!/usr/bin/env python3
"""Consolidate normalized booking events by platform and reservation ID."""

import argparse
import json
from collections import defaultdict
from pathlib import Path


FINAL_EVENTS = {"confirmed", "confirmed_change", "confirmed_extension"}


def consolidate(events):
    unique = {}
    for event in events:
        key = event.get("message_id") or json.dumps(event, ensure_ascii=False, sort_keys=True)
        unique[key] = event
    groups = defaultdict(list)
    for event in unique.values():
        platform = str(event.get("platform", "")).strip()
        reservation_id = str(event.get("reservation_id", "")).strip()
        if not platform or not reservation_id:
            raise ValueError("Every event requires platform and reservation_id")
        groups[(platform, reservation_id)].append(event)

    output = []
    for (platform, reservation_id), rows in sorted(groups.items()):
        rows.sort(key=lambda x: str(x.get("received_at", "")))
        amount = None
        status = "unresolved"
        increments = 0
        for row in rows:
            kind = row.get("event")
            if kind == "pending_change":
                continue
            if kind in FINAL_EVENTS:
                value = row.get("amount")
                if value is not None:
                    if row.get("amount_type") == "increment":
                        increments += value
                        amount = (amount or 0) + value
                    else:
                        amount = value
                status = kind
            elif kind == "cancel":
                if row.get("cancel_fee") is not None:
                    amount = row["cancel_fee"]
                    status = "cancelled_fee_confirmed"
                elif row.get("refund") is not None and amount is not None:
                    amount -= row["refund"]
                    status = "cancelled_refund_confirmed"
                else:
                    amount = None
                    status = "cancelled_refund_unresolved"
            elif kind == "refund_confirmed" and amount is not None:
                amount -= row.get("refund", 0)
                status = "cancelled_refund_confirmed"
        latest = rows[-1]
        output.append({
            "platform": platform,
            "reservation_id": reservation_id,
            "space": latest.get("space"),
            "address": latest.get("address"),
            "use_start": latest.get("use_start"),
            "status": status,
            "recognized_amount": amount,
            "event_count": len(rows),
            "source_ids": [x.get("message_id") for x in rows if x.get("message_id")],
        })
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    events = json.loads(args.events.read_text(encoding="utf-8"))
    result = consolidate(events)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
