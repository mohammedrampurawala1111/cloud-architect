#!/usr/bin/env python3
"""Build evals/RESULTS.md tables from eval_harness.py result directories.

Usage: python3 tools/build_results.py OUT.md RESULT_DIR [RESULT_DIR ...]
Later directories win when the same case/arm/run appears twice.
"""

import glob
import json
import os
import sys
from collections import defaultdict


def load(dirs):
    recs = {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            if f.endswith(("aggregate-result.json", ".tools.json")):
                continue
            r = json.load(open(f, encoding="utf-8"))
            recs[(r["case"], r["arm"], r["run"])] = r
    return list(recs.values())


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def fmt(x):
    return "—" if x is None else "%.2f" % x


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    recs = load(dirs)
    by_case = defaultdict(lambda: defaultdict(list))
    for r in recs:
        by_case[r["case"]][r["arm"]].append(r)

    lines = ["| Scenario | With plugin | Baseline | Δ | Plugin failed | Baseline failed |",
             "|---|---|---|---|---|---|"]
    wins = ties = losses = 0
    totals = {"with": [], "without": []}
    for case in sorted(by_case):
        w, b = by_case[case]["with"], by_case[case]["without"]
        sw, sb = mean([r["score"] for r in w]), mean([r["score"] for r in b])
        if sw is not None:
            totals["with"].append(sw)
        if sb is not None:
            totals["without"].append(sb)
        d = None if sw is None or sb is None else sw - sb
        if d is not None:
            wins += d > 0.001
            losses += d < -0.001
            ties += abs(d) <= 0.001

        def failed(rs):
            names = sorted({g["name"] for r in rs for g in r["graders"] if g["scored"] and not g["passed"]})
            return ", ".join(names) or "—"
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            case, fmt(sw), fmt(sb), "—" if d is None else "%+.2f" % d, failed(w), failed(b)))
    lines += ["", "**Mean score:** plugin %s · baseline %s · Δ %+.2f  " % (
        fmt(mean(totals["with"])), fmt(mean(totals["without"])),
        (mean(totals["with"]) or 0) - (mean(totals["without"]) or 0)),
        "**Scenarios:** plugin better %d · tie %d · baseline better %d" % (wins, ties, losses)]

    # Per-grader pass rates
    stats = defaultdict(lambda: {"with": [0, 0], "without": [0, 0]})
    for r in recs:
        for g in r["graders"]:
            if g["scored"]:
                s = stats[g["name"]][r["arm"]]
                s[0] += g["passed"]
                s[1] += 1
    lines += ["", "| Grader | Plugin pass | Baseline pass |", "|---|---|---|"]
    for name in sorted(stats):
        s = stats[name]
        cell = lambda a: "%d/%d" % tuple(s[a]) if s[a][1] else "—"  # noqa: E731
        lines.append("| %s | %s | %s |" % (name, cell("with"), cell("without")))

    # Side channels
    side = ["", "| Arm | Runs | Mean cost (USD) | Mean time (s) | Replies with Mermaid lint errors |",
            "|---|---|---|---|---|"]
    for arm in ("with", "without"):
        rs = [r for r in recs if r["arm"] == arm]
        if rs:
            side.append("| %s | %d | %.2f | %.0f | %d of %d |" % (
                arm, len(rs), mean([r["cost"] for r in rs]), mean([r["seconds"] for r in rs]),
                sum(1 for r in rs if r.get("mermaid_errors")), sum(1 for r in rs if r.get("mermaid_blocks"))))
    lines += side
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
