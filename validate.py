#!/usr/bin/env python3
"""Checks the shared price files. Run by GitHub on every change.

    python3 validate.py            check every file under data/
    python3 validate.py --actor <account> --changed <file> [<file> ...]
                                   also check that the files changed belong to that account

Exit code 0 when everything is in order.
"""
import json, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 3_000_000
OWNER = "t-more"


def problems_in(path, contributors):
    out = []
    rel = path.relative_to(ROOT)
    match = re.fullmatch(r"data/[a-z0-9-]+/([A-Za-z0-9-]+)\.cg\.json", rel.as_posix())
    if not match:
        return ["%s: files must be data/<auction house>/<github account>.cg.json" % rel]
    account = match.group(1)
    entry = next((v for k, v in contributors.items() if k.lower() == account.lower()), None)
    if entry is None:
        out.append("%s: %s is not in contributors.json" % (rel, account))
    if path.stat().st_size > MAX_BYTES:
        out.append("%s: larger than %d bytes" % (rel, MAX_BYTES))
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        return out + ["%s: not valid JSON (%s)" % (rel, error)]
    if not isinstance(data, dict) or data.get("format") != "craftgraph-prices":
        return out + ["%s: not CraftGraph prices" % rel]
    if str(data.get("github", "")).lower() != account.lower():
        out.append("%s: says it is from GitHub account %r" % (rel, data.get("github")))
    if entry is not None and data.get("from") not in entry.get("characters", []):
        out.append("%s: character %r is not listed for %s" % (rel, data.get("from"), account))
    if not isinstance(data.get("made"), (int, float)) or data["made"] > time.time() + 3600:
        out.append("%s: its time is missing or in the future" % rel)
    items = data.get("items")
    if not isinstance(items, dict) or not items:
        return out + ["%s: holds no items" % rel]
    for key, item in items.items():
        ladder = item.get("l") if isinstance(item, dict) else None
        good = (key.isdigit() and isinstance(item.get("t"), (int, float)) and isinstance(ladder, list)
                and len(ladder) >= 2 and len(ladder) % 2 == 0
                and all(isinstance(x, (int, float)) and x >= 0 for x in ladder))
        if not good:
            out.append("%s: item %s is malformed" % (rel, key))
            break
    return out


def main():
    args = sys.argv[1:]
    contributors = json.loads((ROOT / "contributors.json").read_text(encoding="utf-8"))
    problems = []
    for path in sorted((ROOT / "data").rglob("*")):
        if path.is_file() and path.name != ".gitkeep":
            problems += problems_in(path, contributors)
    if "--actor" in args:
        actor = args[args.index("--actor") + 1]
        changed = args[args.index("--changed") + 1:] if "--changed" in args else []
        for name in changed:
            if name.startswith("data/") and actor.lower() != OWNER.lower():
                if not name.lower().endswith("/%s.cg.json" % actor.lower()):
                    problems.append("%s was changed by %s, who may only change their own file" % (name, actor))
            elif not name.startswith("data/") and actor.lower() != OWNER.lower():
                problems.append("%s was changed by %s; only the owner changes anything outside data/" % (name, actor))
    for line in problems:
        print("PROBLEM: " + line)
    print("%d problem(s)" % len(problems))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
