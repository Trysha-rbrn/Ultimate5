#!/usr/bin/env python3
"""
Interactively fill in the `roles` column of a 5-stack players CSV.

Walks the CSV and, the first time it meets a player name with no role, asks you
for the role(s). It then assigns those roles to EVERY row with that same name
(e.g. every year donk appears), so you only answer once per player.

Players that already have a role on any row are filled in automatically from
that existing value — no prompt. Progress is saved after every answer, so you
can quit (q) and resume later by re-running.

Usage:
    python3 assign_roles.py players_2025.csv          # edits the file in place
    python3 assign_roles.py players.csv -o filled.csv # write to a new file

At each prompt enter role numbers (e.g. "2 3"), role names ("AWP|Pack Rifler"),
Enter to skip, or q to save and quit.
"""

import argparse
import csv
import re
import sys

ROLES = ["IGL", "AWP", "Pack Rifler", "Anchor"]


def resolve_role(token: str):
    """Match a typed fragment to a canonical role name, case-insensitively."""
    t = token.strip().lower()
    if not t:
        return None
    exact = [r for r in ROLES if r.lower() == t]
    if exact:
        return exact[0]
    hits = [r for r in ROLES if t in r.lower()]
    return hits[0] if len(hits) == 1 else None


def parse_input(s: str):
    """Return list of roles, None to skip, or 'QUIT'. Raises ValueError on bad input."""
    s = s.strip()
    if not s:
        return None
    if s.lower() in ("q", "quit", "exit"):
        return "QUIT"

    if re.fullmatch(r"[0-9 ,]+", s):                       # number selection
        roles = []
        for n in (int(x) for x in re.split(r"[ ,]+", s) if x):
            if not 1 <= n <= len(ROLES):
                raise ValueError(f"no option {n}")
            roles.append(ROLES[n - 1])
    else:                                                  # name selection
        roles = []
        for part in (p for p in re.split(r"[|,]", s) if p.strip()):
            r = resolve_role(part)
            if not r:
                raise ValueError(f"unknown role: {part.strip()!r}")
            roles.append(r)

    seen, out = set(), []                                  # de-dupe, keep order
    for r in roles:
        if r not in seen:
            seen.add(r)
            out.append(r)
    if not out:
        raise ValueError("no roles given")
    if len(out) > 2:
        print("  (note: players normally have 1–2 roles)", file=sys.stderr)
    return out


def save(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="Fill the roles column of a 5-stack CSV")
    ap.add_argument("csv", help="players CSV (name,nationality,year,rating,roles)")
    ap.add_argument("-o", "--out", help="output path (default: edit in place)")
    args = ap.parse_args()
    out_path = args.out or args.csv

    with open(args.csv, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if r]

    col = {name: i for i, name in enumerate(header)}
    iname, iroles = col["name"], col["roles"]
    iyear = col.get("year")
    irating = col.get("rating")
    inat = col.get("nationality")

    # 1) seed known roles from any row that already has them, and apply to blanks
    known = {}
    for r in rows:
        val = r[iroles].strip()
        if val:
            known.setdefault(r[iname], val)
    for r in rows:
        if not r[iroles].strip() and r[iname] in known:
            r[iroles] = known[r[iname]]

    # 2) ordered list of names still missing a role
    todo, seen = [], set()
    for r in rows:
        n = r[iname]
        if not r[iroles].strip() and n not in seen:
            seen.add(n)
            todo.append(n)

    if not todo:
        print("Every player already has a role. Nothing to do.")
        save(out_path, header, rows)
        return

    print(f"{len(todo)} player(s) need roles. Options:")
    for i, role in enumerate(ROLES, 1):
        print(f"  {i}) {role}")
    print("Enter numbers (e.g. '2 3'), names ('AWP|Anchor'), blank to skip, q to quit.\n")

    done = 0
    for idx, name in enumerate(todo, 1):
        instances = [r for r in rows if r[iname] == name]
        bits = []
        for r in instances:
            yr = r[iyear] if iyear is not None else "?"
            rt = r[irating] if irating is not None else "?"
            bits.append(f"{yr}:{rt}")
        nat = instances[0][inat] if inat is not None else ""
        ctx = f" [{nat}]" if nat else ""
        print(f"({idx}/{len(todo)}) {name}{ctx}  —  {len(instances)} row(s): {', '.join(bits)}")

        while True:
            try:
                raw = input("  roles> ")
            except (EOFError, KeyboardInterrupt):
                print("\nStopping — progress saved.")
                save(out_path, header, rows)
                return
            try:
                result = parse_input(raw)
            except ValueError as e:
                print(f"  ! {e}. Try again.")
                continue
            break

        if result == "QUIT":
            print("Saving and quitting.")
            save(out_path, header, rows)
            print(f"Done {done} player(s) this session. Re-run to continue.")
            return
        if result is None:
            print("  skipped.\n")
            continue

        roles_str = "|".join(result)
        for r in instances:
            r[iroles] = roles_str
        done += 1
        save(out_path, header, rows)        # save after every answer
        print(f"  -> {roles_str}  (applied to {len(instances)} row(s))\n")

    remaining = sum(1 for r in rows if not r[iroles].strip())
    print(f"Finished. Assigned {done} player(s); {remaining} row(s) still blank.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
