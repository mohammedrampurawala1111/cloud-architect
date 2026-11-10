#!/usr/bin/env python3
"""Check architecture options against the organisation's guardrails (cloud-architect).

The org profile (.cloud-architect/org.yaml) lists what the platform team
already runs and allows: clouds, regions, approved services, forbidden
component classes. Every component that falls outside it needs an exception
ADR. The script only compares; it never decides whether an exception is
acceptable.

Input: one YAML or JSON document with an "org" object and an "options" list,
or the org profile as the file argument and the options via --options.
Standard library only; no network access.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import COMPONENT_CLASSES, InputError, fail, load_data  # noqa: E402

LIST_FIELDS = ("clouds", "regions", "approved_services", "approved_classes", "forbidden_classes")


def _norm(x):
    return " ".join(str(x).lower().replace("-", " ").replace("_", " ").split())


def _list(org, key):
    v = org.get(key)
    if v is None:
        return None
    if not isinstance(v, list) or not all(isinstance(i, (str, int, float)) and not isinstance(i, bool) for i in v):
        raise InputError("org.%s must be a list of names" % key)
    return v


def load_org(doc):
    if not isinstance(doc, dict):
        raise InputError("input must be an object with an 'org' key (or the org profile itself)")
    org = doc.get("org", doc if "org" not in doc and "options" not in doc else None)
    if not isinstance(org, dict):
        raise InputError("missing 'org' object")
    lists = {k: _list(org, k) for k in LIST_FIELDS}
    for k in ("approved_classes", "forbidden_classes"):
        for c in lists[k] or []:
            if c not in COMPONENT_CLASSES:
                raise InputError("org.%s: unknown class %r (see team_score.py --list-classes)" % (k, c))
    if not any(lists.values()):
        raise InputError("org profile has no guardrails: give at least one of %s" % ", ".join(LIST_FIELDS))
    return org, lists


def check_component(comp, opt, lists, where):
    if not isinstance(comp, dict):
        raise InputError("%s must be an object" % where)
    name = comp.get("name") or comp.get("capability") or "component"
    cloud = comp.get("provider", opt.get("provider"))
    region = comp.get("region", opt.get("region"))
    product, cls = comp.get("product"), comp.get("class")
    if cls is not None and cls not in COMPONENT_CLASSES:
        raise InputError("%s: unknown class %r (see team_score.py --list-classes)" % (where, cls))
    findings = []

    def need(rule, detail):
        findings.append({"rule": rule, "detail": detail})

    if lists["clouds"] is not None:
        if cloud is None:
            need("cloud", "provider not given; can't confirm it is one of %s" % ", ".join(map(str, lists["clouds"])))
        elif _norm(cloud) not in {_norm(c) for c in lists["clouds"]}:
            need("cloud", "%s is not an approved cloud (%s)" % (cloud, ", ".join(map(str, lists["clouds"]))))
    if lists["regions"] is not None and comp.get("global") is not True:
        if region is None:
            need("region", "region not given; can't confirm it is one of %s" % ", ".join(map(str, lists["regions"])))
        elif _norm(region) not in {_norm(r) for r in lists["regions"]}:
            need("region", "%s is not an approved region (%s)" % (region, ", ".join(map(str, lists["regions"]))))
    if lists["forbidden_classes"] is not None and cls in lists["forbidden_classes"]:
        need("forbidden class", "%s is forbidden by the org profile" % cls)
    approved_product = (product is not None and lists["approved_services"] is not None
                        and _norm(product) in {_norm(s) for s in lists["approved_services"]})
    approved_class = lists["approved_classes"] is not None and cls in lists["approved_classes"]
    if (lists["approved_services"] is not None or lists["approved_classes"] is not None) \
            and not (approved_product or approved_class) \
            and not (cls is not None and lists["forbidden_classes"] is not None and cls in lists["forbidden_classes"]):
        what = product or cls or "unnamed product"
        need("approved services", "%s is not on the approved list" % what)
    return {"name": name, "product": product, "class": cls, "provider": cloud, "region": region,
            "status": "exception" if findings else "ok", "findings": findings}


def run(doc, options_doc=None):
    org, lists = load_org(doc)
    options = doc.get("options") if isinstance(doc, dict) else None
    if options_doc is not None:
        options = options_doc.get("options") if isinstance(options_doc, dict) else options_doc
    if not isinstance(options, list) or not options:
        raise InputError("'options' must be a non-empty list")
    results = []
    for i, opt in enumerate(options):
        where = "options[%d]" % i
        if not isinstance(opt, dict):
            raise InputError("%s must be an object" % where)
        comps = opt.get("components")
        if not isinstance(comps, list) or not comps:
            raise InputError("%s.components must be a non-empty list" % where)
        rows = [check_component(c, opt, lists, "%s.components[%d]" % (where, j)) for j, c in enumerate(comps)]
        n = sum(1 for r in rows if r["status"] == "exception")
        results.append({"name": opt.get("name") or "Option %d" % (i + 1), "exceptions": n,
                        "verdict": "fits guardrails" if n == 0 else "needs %d exception ADR%s" % (n, "" if n == 1 else "s"),
                        "components": rows})
    return {"org": org.get("name"), "guardrails": {k: v for k, v in lists.items() if v is not None},
            "platform": org.get("platform"), "policies": org.get("policies"), "options": results}


def to_markdown(r):
    lines = ["**Org guardrails%s**" % (": " + r["org"] if r["org"] else ""), "",
             "| Option | Exceptions | Verdict |", "|---|---|---|"]
    for o in r["options"]:
        lines.append("| %s | %d | %s |" % (o["name"], o["exceptions"], o["verdict"]))
    rows = [(o["name"], c, f) for o in r["options"] for c in o["components"] for f in c["findings"]]
    if rows:
        lines += ["", "| Option | Component | Product | Rule | Why it needs an exception |", "|---|---|---|---|---|"]
        for opt, c, f in rows:
            lines.append("| %s | %s | %s | %s | %s |" % (opt, c["name"], c["product"] or c["class"] or "—",
                                                       f["rule"], f["detail"]))
        lines += ["", "Each exception needs an exception ADR signed off by the org owner, "
                      "or a change to the design."]
    else:
        lines += ["", "Every component fits the org guardrails."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="guardrails.py",
        description="Check architecture options against the org profile: approved clouds, regions, "
                    "services and forbidden component classes. Lists every component that needs an "
                    "exception ADR.",
        epilog="Example: python3 guardrails.py samples/org.yaml --options samples/guardrail_options.yaml "
               "--format markdown\nExit status: 0 ok (exceptions are reported, not errors), 2 invalid input.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="org profile + options (YAML or JSON); '-' reads stdin")
    ap.add_argument("--options", help="separate YAML/JSON file with an 'options' list")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    try:
        doc = load_data(args.input)
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
