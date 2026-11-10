#!/usr/bin/env python3
"""Deterministic operational-complexity budget for a team (cloud-architect).

Implements the rules in skills/team-fit/SKILL.md exactly:

  start at 1
  +1    >= 2 people will operate the system after launch
  +1    an on-call rotation exists (or will before launch)
  +1    solid (>= 2) container AND IaC experience
  +1    solid (>= 2) Kubernetes experience OR a platform/SRE team
  +0.5  preference = control
  -0.5  preference = managed
  round half up, clamp to 1-5

Option complexity = highest component weight, +1 if the option has more than
8 distinct runtime components. Verdict: within (level <= budget), at_limit
(level = budget + 1), exceeds (level >= budget + 2).

Input: the team profile the interview skill emits, as YAML or JSON, either
with a top-level "team:" key or as the team object itself. An optional
"team.evidence" map records where each fact came from (e.g. "12 Helm charts in
deploy/"); facts without evidence are reported as self-reported. Options may be in
the same file under "options:" or in a separate --options file.
Standard library only; no network access.
"""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import (InputError, classes_by_weight,
                     component_weight, fail, load_data)

MAX_COMPONENTS_BEFORE_PENALTY = 8
SOLID = 2
SKILL_LEVELS = {0: "none", 1: "some", 2: "solid", 3: "expert"}
VERDICT_LABELS = {"within": "Within", "at_limit": "At limit", "exceeds": "Exceeds"}
CLOUD_KEYS = ("aws", "azure", "gcp")
# Factor -> the team fields whose evidence backs it (team.evidence keys).
EVIDENCE_KEYS = {
    ">= 2 operators after launch": ("operators",),
    "on-call rotation": ("on_call",),
    "solid containers and IaC": ("containers", "iac"),
    "solid Kubernetes or platform/SRE team": ("kubernetes", "platform_team"),
    "preference": ("preference",),
}


def _num(value, field, warnings, default=0):
    if value is None:
        warnings.append("%s not given; assumed %s" % (field, default))
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError("%s must be a number, got %r" % (field, value))
    if value < 0:
        raise InputError("%s must not be negative, got %r" % (field, value))
    return value


def _bool(value, field, warnings):
    if value is None:
        warnings.append("%s not given; assumed false" % field)
        return False
    if not isinstance(value, bool):
        raise InputError("%s must be true or false, got %r" % (field, value))
    return value


def _skill(value, field, warnings):
    """A skill is 0-3, or a mapping of tool -> 0-3 (the max counts)."""
    if value is None:
        warnings.append("%s not given; assumed 0 (none)" % field)
        return 0, None
    if isinstance(value, dict):
        if not value:
            warnings.append("%s is empty; assumed 0 (none)" % field)
            return 0, None
        best_tool, best = None, -1
        for tool, lvl in value.items():
            lvl = _skill(lvl, "%s.%s" % (field, tool), warnings)[0]
            if lvl > best:
                best_tool, best = tool, lvl
        return best, best_tool
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 3:
        raise InputError("%s must be 0-3 (or a map of tool: 0-3), got %r" % (field, value))
    return value, None


def round_half_up(x):
    return int(math.floor(x + 0.5))


def extract(doc):
    if not isinstance(doc, dict):
        raise InputError("input must be an object with a 'team' key (or the team object itself)")
    team = doc.get("team", doc if "team" not in doc and ("operators" in doc or "skills" in doc) else None)
    if not isinstance(team, dict):
        raise InputError("missing 'team' object")
    return team, doc.get("options")


def score_team(team):
    """Return (budget, raw, breakdown, warnings, known)."""
    warnings = []
    skills = team.get("skills") or {}
    if not isinstance(skills, dict):
        raise InputError("team.skills must be an object")

    operators = team.get("operators")
    if operators is None and team.get("builders") is not None:
        operators = team.get("builders")
        warnings.append("team.operators not given; used team.builders (%s)" % operators)
    operators = _num(operators, "team.operators", warnings, default=1)
    on_call = _bool(team.get("on_call"), "team.on_call", warnings)
    platform_team = _bool(team.get("platform_team"), "team.platform_team", warnings)
    containers, _ = _skill(skills.get("containers"), "team.skills.containers", warnings)
    iac, iac_tool = _skill(skills.get("iac"), "team.skills.iac", warnings)
    k8s, _ = _skill(skills.get("kubernetes"), "team.skills.kubernetes", warnings)
    pref = team.get("preference")
    if pref is None:
        warnings.append("team.preference not given; assumed balanced")
        pref = "balanced"
    if pref not in ("managed", "balanced", "control"):
        raise InputError("team.preference must be managed, balanced or control, got %r" % pref)

    def lvl(n):
        return "%s (%s)" % (n, SKILL_LEVELS.get(int(n), n))

    breakdown = [
        {"factor": "start", "points": 1, "applied": True, "evidence": "every team starts at 1"},
        {"factor": ">= 2 operators after launch", "points": 1 if operators >= 2 else 0,
         "applied": operators >= 2, "evidence": "operators = %s" % operators},
        {"factor": "on-call rotation", "points": 1 if on_call else 0, "applied": on_call,
         "evidence": "on_call = %s" % str(on_call).lower()},
        {"factor": "solid containers and IaC", "points": 1 if containers >= SOLID and iac >= SOLID else 0,
         "applied": containers >= SOLID and iac >= SOLID,
         "evidence": "containers = %s, IaC = %s%s" % (lvl(containers), lvl(iac),
                                                       " via %s" % iac_tool if iac_tool else "")},
        {"factor": "solid Kubernetes or platform/SRE team",
         "points": 1 if k8s >= SOLID or platform_team else 0,
         "applied": k8s >= SOLID or platform_team,
         "evidence": "kubernetes = %s, platform_team = %s" % (lvl(k8s), str(platform_team).lower())},
        {"factor": "preference", "points": {"control": 0.5, "managed": -0.5}.get(pref, 0),
         "applied": pref != "balanced", "evidence": "preference = %s" % pref},
    ]
    evidence = team.get("evidence") or {}
    if not isinstance(evidence, dict):
        raise InputError("team.evidence must be an object of field: source text")
    unknown = sorted(set(evidence) - {k for keys in EVIDENCE_KEYS.values() for k in keys})
    if unknown:
        raise InputError("team.evidence: unknown field(s) %s (use %s)" % (
            ", ".join(unknown), ", ".join(sorted({k for v in EVIDENCE_KEYS.values() for k in v}))))
    for b in breakdown[1:]:
        found = ["%s: %s" % (k, evidence[k]) for k in EVIDENCE_KEYS[b["factor"]]
                 if evidence.get(k) not in (None, "")]
        b["source"] = "; ".join(found) if found else "self-reported"
    raw = sum(b["points"] for b in breakdown)
    budget = max(1, min(5, round_half_up(raw)))

    known = sorted(
        name for name, v in (
            [(k, skills.get(k)) for k in skills if not isinstance(skills.get(k), dict)]
            + [("%s.%s" % (k, t), lv) for k in skills if isinstance(skills.get(k), dict)
               for t, lv in skills[k].items()]
        )
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= SOLID
    )
    cloud_scores = {c: skills.get(c) for c in CLOUD_KEYS
                    if isinstance(skills.get(c), (int, float)) and not isinstance(skills.get(c), bool)}
    strongest = None
    if cloud_scores:
        top = max(cloud_scores.values())
        leaders = sorted(c for c, v in cloud_scores.items() if v == top)
        strongest = leaders[0] if len(leaders) == 1 and top > 0 else None
    return budget, raw, breakdown, warnings, {"solid_or_better": known, "strongest_cloud": strongest}


def assess_option(opt, budget, idx):
    where = "options[%d]" % idx
    if not isinstance(opt, dict):
        raise InputError("%s must be an object" % where)
    name = opt.get("name") or "Option %d" % (idx + 1)
    comps = opt.get("components")
    if comps is not None:
        if not isinstance(comps, list) or not comps:
            raise InputError("%s.components must be a non-empty list" % where)
        weights = []
        runtime = 0
        for j, comp in enumerate(comps):
            w = component_weight(comp, "%s.components[%d]" % (where, j))
            weights.append(w)
            if comp.get("runtime", True) is not False:
                runtime += 1
        top = max(weights)
        penalty = 1 if runtime > MAX_COMPONENTS_BEFORE_PENALTY else 0
        level = top + penalty
        how = "highest component weight %d%s" % (
            top, ", +1 for %d runtime components (> %d)" % (runtime, MAX_COMPONENTS_BEFORE_PENALTY) if penalty else "")
        detail = {"max_component_weight": top, "runtime_components": runtime, "component_penalty": penalty}
    elif opt.get("complexity") is not None:
        level = opt["complexity"]
        if isinstance(level, bool) or not isinstance(level, int) or level < 1:
            raise InputError("%s.complexity must be a positive integer" % where)
        how = "complexity given directly"
        detail = {}
    else:
        raise InputError("%s needs 'components' or 'complexity'" % where)
    if level <= budget:
        verdict = "within"
    elif level == budget + 1:
        verdict = "at_limit"
    else:
        verdict = "exceeds"
    out = {"name": name, "complexity": level, "verdict": verdict, "basis": how}
    out.update(detail)
    return out


def run(doc, options_doc=None):
    team, options = extract(doc)
    if options_doc is not None:
        options = options_doc.get("options") if isinstance(options_doc, dict) else options_doc
    budget, raw, breakdown, warnings, known = score_team(team)
    result = {
        "budget": budget,
        "raw_score": raw,
        "rounding": "round half up, clamp 1-5",
        "breakdown": breakdown,
        "known_tools": known,
        "options": [],
        "warnings": warnings,
    }
    if options is not None:
        if not isinstance(options, list):
            raise InputError("options must be a list")
        result["options"] = [assess_option(o, budget, i) for i, o in enumerate(options)]
    return result


def _fmt(x):
    return ("%+g" % x) if x else "0"


def to_markdown(r):
    parts = []
    for b in r["breakdown"][1:]:
        parts.append("%s (%s)" % (b["evidence"], _fmt(b["points"])))
    lines = [
        "**Operational complexity budget: %d / 5**" % r["budget"],
        "Reasoning: start 1; %s → %g → %d." % ("; ".join(parts), r["raw_score"], r["budget"]),
    ]
    backed = [b for b in r["breakdown"][1:] if b.get("source", "self-reported") != "self-reported"]
    total = len(r["breakdown"]) - 1
    if not backed:
        lines.append("Evidence: none; all %d factors are self-reported." % total)
    else:
        lines.append("Evidence: %d of %d factors backed (%s)%s." % (
            len(backed), total, "; ".join("%s ← %s" % (b["factor"], b["source"]) for b in backed),
            ", the rest self-reported" if len(backed) < total else ""))
    if r["options"]:
        lines += ["", "| Option | Complexity | Verdict |", "|---|---|---|"]
        for o in r["options"]:
            lines.append("| %s | %d | %s |" % (o["name"], o["complexity"], VERDICT_LABELS[o["verdict"]]))
    if r["warnings"]:
        lines += ["", "Assumptions: " + "; ".join(r["warnings"]) + "."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="team_score.py",
        description="Compute a team's operational complexity budget (1-5) and check "
                    "architecture options against it. Rules: skills/team-fit/SKILL.md.",
        epilog="Example: python3 team_score.py samples/team.yaml --format markdown\n"
               "Exit status: 0 ok, 2 invalid input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("profile", nargs="?", help="team profile (YAML or JSON); '-' reads stdin")
    ap.add_argument("--options", help="separate YAML/JSON file with an 'options' list")
    ap.add_argument("--format", choices=["json", "markdown"], default="json")
    ap.add_argument("--list-classes", action="store_true", help="print component classes and weights")
    args = ap.parse_args(argv)

    if args.list_classes:
        json.dump(classes_by_weight(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if not args.profile:
        ap.error("profile is required (or use --list-classes)")
    try:
        doc = load_data(args.profile)
        options_doc = load_data(args.options) if args.options else None
        result = run(doc, options_doc)
    except InputError as exc:
        return fail(ap.prog, exc)
    if args.format == "markdown":
        sys.stdout.write(to_markdown(result) + "\n")
    else:
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
