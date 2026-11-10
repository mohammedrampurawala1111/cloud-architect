#!/usr/bin/env python3
"""One call for the whole design check (cloud-architect).

Reads one document with the team profile and the mapped options, and prints,
in order:
  1. team fit   - complexity budget and a verdict per option (team_score.py)
  2. guardrails - only when an org profile is given (guardrails.py)

Same rules and output as the two scripts; it only saves tool calls. Input:

    team:            # as for team_score.py
      ...
    org:             # optional inline guardrails, as for guardrails.py
      ...
    options:         # components need class (or weight); product, provider and
      - name: ...    # region (per option or component) when guardrails apply
        components: ...

Or pass the org profile file with --org. Standard library only.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import guardrails  # noqa: E402
import team_score  # noqa: E402
from _common import InputError, fail, load_data  # noqa: E402


def run(doc, org_doc=None):
    if not isinstance(doc, dict):
        raise InputError("input must be an object with 'team' and 'options'")
    if not isinstance(doc.get("options"), list) or not doc["options"]:
        raise InputError("'options' must be a non-empty list")
    try:
        team = team_score.run(doc)
    except InputError as exc:
        raise InputError("team fit: %s" % exc)
    rails = None
    org = org_doc if org_doc is not None else ({"org": doc["org"]} if "org" in doc else None)
    if org is not None:
        try:
            rails = guardrails.run(org, {"options": doc["options"]})
        except InputError as exc:
            raise InputError("guardrails: %s" % exc)
    return {"team_fit": team, "guardrails": rails}


def to_markdown(r):
    parts = ["### Team fit", "", team_score.to_markdown(r["team_fit"])]
    if r["guardrails"] is not None:
        parts += ["", "### Org guardrails", "", guardrails.to_markdown(r["guardrails"])]
    return "\n".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="plan.py",
        description="Team fit and (optionally) org guardrails for all options in one call.",
        epilog="Example: python3 plan.py samples/plan.yaml --org samples/org.yaml\n"
               "Exit status: 0 ok, 2 invalid input.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="team + options (YAML or JSON); '-' reads stdin")
    ap.add_argument("--org", metavar="PATH", help="org profile file (e.g. .cloud-architect/org.yaml)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)
    try:
        doc = load_data(args.input)
        org_doc = load_data(args.org) if args.org else None
        res = run(doc, org_doc)
    except InputError as exc:
        return fail(ap.prog, exc)
    if args.format == "json":
        json.dump(res, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(to_markdown(res) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
