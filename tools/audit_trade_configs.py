#!/usr/bin/env python3
"""Audit Anomaly trade_*.ltx files for weekly stock review.

The script is intentionally standalone Python and does not execute game Lua.
It checks changed trade configs by default (`git diff --name-only`) and falls
back to every gamedata/configs/items/trade/trade_*.ltx file when git metadata is
unavailable or no changed trade configs are found.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

PROGRESSION_WORDS = ("goodwill", "rank", "reputation", "heavy_pockets", "heavy pockets", "has_achievement", "actor_has_story")
ITEM_RE = re.compile(r"^([^;#\s][^=]*?)\s*=\s*([^;#]+)")
SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]")


def changed_trade_files(root: Path) -> list[Path]:
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", "HEAD", "--", "gamedata/configs/items/trade/trade_*.ltx"], cwd=root, text=True)
    except Exception:
        out = ""
    files = [root / line.strip() for line in out.splitlines() if line.strip()]
    files = [p for p in files if p.exists()]
    if files:
        return files
    return sorted((root / "gamedata/configs/items/trade").glob("trade_*.ltx"))


def parse_ltx(path: Path):
    sections: dict[str, list[tuple[int, str, str]]] = {}
    current = None
    for lineno, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        m = SECTION_RE.match(raw)
        if m:
            current = m.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append((lineno, raw.strip(), raw))
    return sections


def parse_qty_prob(value: str) -> tuple[float | None, float | None]:
    parts = [p.strip() for p in value.split(",")]
    qty = prob = None
    if parts:
        try: qty = float(parts[0])
        except ValueError: pass
    if len(parts) > 1:
        try: prob = float(parts[1])
        except ValueError: pass
    return qty, prob


def category(item: str) -> str:
    if item.startswith("ammo_"): return "ammo"
    if item.startswith("wpn_"): return "weapon"
    if "outfit" in item or item.startswith("helm_"): return "armor"
    if "detector" in item or "tool" in item or "device" in item: return "device/tool"
    if item.startswith(("medkit", "bandage", "drug_", "stimpack", "antirad")): return "medical"
    if item.startswith(("bread", "kolbasa", "conserva", "vodka", "water", "energy_drink")): return "consumable"
    return "other"


def audit_file(path: Path):
    sections = parse_ltx(path)
    errors = []
    rows = []
    if "trader" not in sections:
        errors.append(f"{path}: missing [trader]")
        return rows, errors
    buy_line = next((line for _, line, _ in sections["trader"] if line.startswith("buy_supplies")), "")
    if not buy_line:
        errors.append(f"{path}: [trader] missing buy_supplies")
        return rows, errors
    buy_value = buy_line.split("=", 1)[1].strip()
    if any(w in buy_value.lower() for w in PROGRESSION_WORDS) or "{" in buy_value:
        errors.append(f"{path}: progression condlist remains in buy_supplies: {buy_value}")
    target = buy_value.split(",")[-1].strip().split()[-1]
    if target not in sections:
        errors.append(f"{path}: buy_supplies points to missing section [{target}]")
        return rows, errors
    seen = {}
    for lineno, line, raw in sections[target]:
        m = ITEM_RE.match(line)
        if not m or line.startswith("buy_supplies"):
            continue
        item = m.group(1).strip()
        value = m.group(2).strip()
        if item in seen:
            errors.append(f"{path}:{lineno}: duplicate item {item} also seen at line {seen[item]}")
        seen[item] = lineno
        qty, prob = parse_qty_prob(value)
        if qty is None or qty <= 0:
            errors.append(f"{path}:{lineno}: non-positive or invalid quantity for {item}: {value}")
        if prob is None or not (0 <= prob <= 1):
            errors.append(f"{path}:{lineno}: probability outside 0..1 for {item}: {value}")
        rows.append({"trader": path.stem, "item": item, "quantity": qty, "probability": prob, "source old tier": "merged supplies_1..supplies_5", "category": category(item)})
    return rows, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=("csv", "markdown"), default="markdown")
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args()
    all_rows, all_errors = [], []
    files = changed_trade_files(args.root)
    for path in files:
        rows, errors = audit_file(path)
        all_rows.extend(rows); all_errors.extend(errors)
    if args.format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=["trader", "item", "quantity", "probability", "source old tier", "category"])
        writer.writeheader(); writer.writerows(all_rows)
    else:
        print("| trader | item | quantity | probability | source old tier | category |")
        print("| --- | --- | ---: | ---: | --- | --- |")
        for r in all_rows:
            print(f"| {r['trader']} | {r['item']} | {r['quantity']} | {r['probability']} | {r['source old tier']} | {r['category']} |")
    for err in all_errors:
        print(f"ERROR: {err}", file=sys.stderr)
    return 1 if all_errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
