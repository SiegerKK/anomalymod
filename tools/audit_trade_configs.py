#!/usr/bin/env python3
"""Audit Anomaly/AOEngine trade LTX and DLTX weekly stock patches.

The auditor reads vanilla ``trade_*.ltx`` sources and ``mod_trade_*.ltx`` DLTX
patches, applies the subset of DLTX needed by the weekly stock layer, resolves
section inheritance, and emits the effective commercial assortment.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

SECTION_RE = re.compile(r"^\s*([!@]?)\[([^\]]+)\](?::\s*([^;#]+))?")
INCLUDE_RE = re.compile(r'^\s*#include\s+["<]([^">]+)[">]')
ITEM_RE = re.compile(r"^\s*([^;#\s][^=]*?)\s*=\s*([^;#]+)")
TIERS = tuple(f"supplies_{i}" for i in range(1, 6))
PROGRESSION_WORDS = ("goodwill", "rank", "reputation", "heavy_pockets", "has_achievement", "actor_has_story")

@dataclass
class Entry:
    key: str
    value: str
    file: Path
    line: int

@dataclass
class Section:
    name: str
    op: str = ""
    parents: list[str] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)
    file: Path | None = None
    line: int = 0

@dataclass
class Profile:
    name: str
    sections: dict[str, Section] = field(default_factory=dict)
    sources: list[Path] = field(default_factory=list)


def strip_comment(line: str) -> str:
    return line.split(";", 1)[0].split("#", 1)[0].strip()


def read_with_includes(path: Path, seen: set[Path] | None = None) -> list[tuple[Path, int, str]]:
    seen = seen or set()
    path = path.resolve()
    if path in seen or not path.exists():
        return []
    seen.add(path)
    rows: list[tuple[Path, int, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        m = INCLUDE_RE.match(raw)
        if m:
            include_path = m.group(1).replace("\\", "/")
            inc = (path.parent / include_path).resolve()
            rows.extend(read_with_includes(inc, seen))
        rows.append((path, lineno, raw))
    return rows


def parse_file(path: Path) -> list[Section]:
    sections: list[Section] = []
    current: Section | None = None
    for src, lineno, raw in read_with_includes(path):
        m = SECTION_RE.match(raw)
        if m:
            op, name, parents = m.groups()
            current = Section(name=name.strip(), op=op, parents=[p.strip() for p in (parents or "").split(",") if p.strip()], file=src, line=lineno)
            sections.append(current)
            continue
        if current:
            kv = ITEM_RE.match(raw)
            if kv:
                current.entries.append(Entry(kv.group(1).strip(), kv.group(2).strip(), src, lineno))
    return sections


def profile_name(path: Path) -> str:
    stem = path.stem
    if stem.startswith("mod_") and stem.endswith("_weekly_stock"):
        return stem[4:-13]
    return stem


def load_profiles(root: Path, source_root: Path | None) -> dict[str, Profile]:
    roots = []
    if source_root:
        roots.append(source_root / "gamedata/configs/items/trade")
        roots.append(source_root / "configs/items/trade")
    roots.append(root / "gamedata/configs/items/trade")
    profiles: dict[str, Profile] = {}
    for trade_dir in roots:
        if not trade_dir.exists():
            continue
        files = sorted(set(trade_dir.glob("trade_*.ltx")) | set(trade_dir.glob("mod_trade_*.ltx")), key=lambda p: (p.name.startswith("mod_"), p.name))
        for path in files:
            name = profile_name(path)
            prof = profiles.setdefault(name, Profile(name))
            prof.sources.append(path)
            for sec in parse_file(path):
                if sec.op == "!":
                    target = prof.sections.setdefault(sec.name, Section(sec.name))
                    target.entries = [e for e in target.entries if e.key not in {x.key for x in sec.entries}]
                    target.entries.extend(sec.entries)
                    if sec.parents:
                        target.parents = sec.parents
                else:
                    prof.sections[sec.name] = sec
    return profiles


def resolve_section(prof: Profile, name: str, stack: tuple[str, ...] = ()) -> OrderedDict[str, Entry]:
    if name in stack:
        raise ValueError(f"inheritance cycle: {' -> '.join(stack + (name,))}")
    sec = prof.sections.get(name)
    if not sec:
        raise KeyError(name)
    out: OrderedDict[str, Entry] = OrderedDict()
    for parent in sec.parents:
        out.update(resolve_section(prof, parent, stack + (name,)))
    for e in sec.entries:
        out[e.key] = e
    return out


def parse_qty_prob(value: str) -> tuple[float | None, float | None, str | None]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None, None, f"malformed supply entry: {value}"
    try:
        qty = float(parts[0])
    except ValueError:
        return None, None, f"quantity is not numeric: {value}"
    try:
        prob = float(parts[1])
    except ValueError:
        return None, None, f"probability is not numeric: {value}"
    if qty <= 0:
        return qty, prob, f"quantity must be > 0: {value}"
    if prob < 0 or prob > 1:
        return qty, prob, f"probability must be between 0 and 1: {value}"
    return qty, prob, None


def category(item: str) -> str:
    if item.startswith("ammo_"): return "ammo"
    if item.startswith("wpn_"): return "weapon"
    if "outfit" in item or item.startswith("helm_"): return "armor"
    if item.startswith(("medkit", "bandage", "drug_", "stimpack", "antirad")): return "medical"
    if item.startswith(("bread", "kolbasa", "conserva", "vodka", "water", "energy_drink")): return "consumable"
    if "detector" in item or "tool" in item or "device" in item: return "device/tool"
    return "other"


def audit(profiles: dict[str, Profile]):
    rows, errors = [], []
    audited = 0
    for prof in sorted(profiles.values(), key=lambda p: p.name):
        if "trader" not in prof.sections:
            continue
        audited += 1
        trader = resolve_section(prof, "trader")
        buy = trader.get("buy_supplies")
        if not buy:
            errors.append(f"{prof.name}: [trader] has no buy_supplies")
            continue
        target = buy.value.split(",")[-1].strip().split()[-1]
        if any(w in buy.value.lower() for w in PROGRESSION_WORDS) or "{" in buy.value:
            errors.append(f"{prof.name}: progression condlist remains in buy_supplies: {buy.value}")
        if target not in prof.sections:
            errors.append(f"{prof.name}: buy_supplies points to missing section [{target}]")
            continue
        if target == "supplies_weekly":
            missing = [p for p in prof.sections[target].parents if p not in prof.sections]
            if missing:
                errors.append(f"{prof.name}: supplies_weekly inherits missing section(s): {', '.join(missing)}")
        item_sources = defaultdict(list)
        value_chains = defaultdict(list)
        for tier in TIERS:
            if tier in prof.sections:
                direct_seen = set()
                for ent in prof.sections[tier].entries:
                    if ent.key in direct_seen:
                        errors.append(f"{prof.name}: duplicate declaration for {ent.key} inside [{tier}] at {ent.file}:{ent.line}")
                    direct_seen.add(ent.key)
                    item_sources[ent.key].append(tier)
                    value_chains[ent.key].append(f"{tier}={ent.value}")
        try:
            effective = resolve_section(prof, target)
        except KeyError as exc:
            errors.append(f"{prof.name}: missing parent section [{exc.args[0]}]")
            continue
        for item, ent in effective.items():
            if item == "buy_supplies":
                continue
            qty, prob, parse_error = parse_qty_prob(ent.value)
            if parse_error:
                errors.append(f"{prof.name}: {item}: {parse_error} at {ent.file}:{ent.line}")
            tiers = item_sources.get(item) or [target]
            rows.append({"trader": prof.name, "item": item, "quantity": qty if qty is not None else "", "probability": prob if prob is not None else "", "original_tiers": "+".join(tiers), "effective_section": target, "category": category(item)})
    if audited == 0:
        errors.append("no trade profiles found")
    return rows, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--source-root", type=Path, help="AOEngine/Anomaly 1.5.3 source root with gamedata or configs")
    ap.add_argument("--format", choices=("markdown", "csv"), default="markdown")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    rows, errors = audit(load_profiles(args.root, args.source_root))
    out = []
    if args.format == "csv":
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["trader", "item", "quantity", "probability", "original_tiers", "effective_section", "category"])
        writer.writeheader(); writer.writerows(rows)
        text = buf.getvalue()
    else:
        out.append("| trader | item | quantity | probability | original_tiers | effective_section | category |")
        out.append("| --- | --- | ---: | ---: | --- | --- | --- |")
        for r in rows:
            out.append(f"| {r['trader']} | {r['item']} | {r['quantity']} | {r['probability']} | {r['original_tiers']} | {r['effective_section']} | {r['category']} |")
        text = "\n".join(out) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
