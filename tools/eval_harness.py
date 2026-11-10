#!/usr/bin/env python3
"""Stand-in runner for `claude plugin eval` (development tool, not shipped in the plugin).

`claude plugin eval` is in early access and refuses to run on accounts without it.
This script runs the same case files (evals/<case>/prompt.md + graders/*.md) with
the same semantics, so the suite can be used now and moved to the official runner
unchanged later:

  * two arms per case: "with" (--plugin-dir <plugin>) and "without" (no plugin);
  * each run in a fresh empty temp directory with user settings, user plugins and
    MCP servers excluded (--setting-sources project --strict-mcp-config);
  * graders: regex (target last_message|trace, match contains|not_contains|count:N,
    flags), tool_used (tool, input_match, min, max, arm), llm (focus last_message,
    weight). `arm: with-only` graders are reported, never scored;
  * llm graders for one run are judged together in a single blind call (the judge
    doesn't know the arm) by a different model from the agent;
  * an extra, unscored metric runs scripts/check_mermaid.py on every reply.

Usage:
  python3 tools/eval_harness.py plugins/cloud-architect --runs 1 --max-cost 60   # cases in evals/
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

LOCK = threading.Lock()
SPENT = [0.0]

JUDGE_SYSTEM = (
    "You are a strict, terse evaluation judge for AI assistant answers about software "
    "architecture. You receive numbered criteria and an answer. Judge each criterion "
    "independently and literally against the answer text only. Reply with JSON only: "
    '{"<criterion name>": {"verdict": "PASS" | "FAIL", "reason": "<one sentence>"}, ...}'
)


def parse_front(text, loads):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = loads(text[3:end]) or {}
            return fm, text[end + 4:].lstrip("\n")
    return {}, text


def load_cases(eval_dir, loads, pattern=None):
    cases = []
    for name in sorted(os.listdir(eval_dir)):
        d = os.path.join(eval_dir, name)
        p = os.path.join(d, "prompt.md")
        if not os.path.isfile(p) or (pattern and not re.search(pattern, name)):
            continue
        fm, body = parse_front(open(p, encoding="utf-8").read(), loads)
        graders = []
        gdir = os.path.join(d, "graders")
        for g in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
            if g.endswith(".md"):
                gfm, gbody = parse_front(open(os.path.join(gdir, g), encoding="utf-8").read(), loads)
                graders.append({"name": g[:-3], "fm": gfm, "body": gbody.strip()})
        fx = os.path.normpath(os.path.join(d, fm["fixture"])) if fm.get("fixture") else None
        if fx and not os.path.isdir(fx):
            raise SystemExit("%s: fixture %s not found" % (name, fx))
        cases.append({"name": name, "fm": fm, "prompt": body.strip(), "graders": graders, "fixture": fx})
    return cases


def run_agent(case, arm, plugin, model, budget):
    fm = case["fm"]
    allowed = fm.get("allowed_tools") or ["Read", "Skill"]
    tools = sorted({re.sub(r"\(.*", "", t) for t in allowed})
    cmd = ["claude", "-p", case["prompt"], "--model", model, "--output-format", "stream-json",
           "--verbose", "--no-session-persistence", "--setting-sources", "project",
           "--strict-mcp-config", "--tools", ",".join(tools),
           "--allowedTools", *allowed, "--max-turns", str(fm.get("max_turns", 10)),
           "--max-budget-usd", str(budget)]
    if arm == "with":
        cmd += ["--plugin-dir", plugin]
    cwd = tempfile.mkdtemp(prefix="ca-eval-")
    if case.get("fixture"):   # a repository the agent works in (both arms get the same copy)
        shutil.copytree(case["fixture"], cwd, dirs_exist_ok=True)
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=fm.get("timeout_seconds", 600))
        out, timed_out = proc.stdout, False
    except subprocess.TimeoutExpired as exc:
        out, timed_out = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""), True
    events, tool_uses, last_text, result = [], [], "", {}
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        events.append(ev)
        if ev.get("type") == "assistant" and ev.get("parent_tool_use_id") is None:
            texts = []
            for blk in ev.get("message", {}).get("content", []):
                if blk.get("type") == "tool_use":
                    tool_uses.append({"name": blk.get("name"), "input": blk.get("input")})
                elif blk.get("type") == "text":
                    texts.append(blk.get("text", ""))
            if texts:
                last_text = "\n".join(texts)
        if ev.get("type") == "user":
            for blk in ev.get("message", {}).get("content", []) or []:
                if isinstance(blk, dict) and blk.get("type") == "tool_result":
                    c = blk.get("content")
                    text = c if isinstance(c, str) else json.dumps(c)
                    if tool_uses and "result" not in tool_uses[-1]:
                        tool_uses[-1]["result"] = text[:800]
        if ev.get("type") == "result":
            result = ev
    final = result.get("result") if isinstance(result.get("result"), str) and result.get("result") else last_text
    return {
        "arm": arm, "cwd": cwd, "seconds": round(time.time() - t0, 1), "timed_out": timed_out,
        "cost": result.get("total_cost_usd", 0.0) or 0.0, "turns": result.get("num_turns"),
        "is_error": result.get("is_error", True) or timed_out, "last_message": final or "",
        "tool_uses": tool_uses, "trace": "\n".join(json.dumps(e) for e in events),
    }


def judge(criteria, answer, model):
    if not criteria:
        return {}, 0.0
    parts = ["Criteria:"]
    for i, (name, text) in enumerate(criteria, 1):
        parts.append("%d. %s: %s" % (i, name, text))
    parts += ["", "Answer to judge:", "<answer>", answer[:120000], "</answer>",
              "", "Reply with the JSON object only, keyed by criterion name."]
    cmd = ["claude", "-p", "\n".join(parts), "--model", model, "--system-prompt", JUDGE_SYSTEM,
           "--tools", "", "--output-format", "json", "--no-session-persistence",
           "--setting-sources", "project", "--strict-mcp-config"]
    proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
    try:
        res = json.loads(proc.stdout)
        text = res.get("result", "")
        m = re.search(r"\{.*\}", text, re.S)
        verdicts = json.loads(m.group(0)) if m else {}
        return verdicts, res.get("total_cost_usd", 0.0) or 0.0
    except (ValueError, AttributeError):
        return {}, 0.0


def grade(case, run, judge_model, check_mermaid):
    results, llm_criteria = [], []
    for g in case["graders"]:
        fm, kind = g["fm"], g["fm"].get("type")
        weight = float(fm.get("weight", 1))
        if kind == "regex":
            target = run["trace"] if fm.get("target") == "trace" else run["last_message"]
            flags = 0
            for f in str(fm.get("flags", "")):
                flags |= {"i": re.I, "m": re.M, "s": re.S}.get(f, 0)
            n = len(re.findall(g["body"], target, flags))
            match = str(fm.get("match", "contains"))
            if match == "contains":
                ok = n > 0
            elif match == "not_contains":
                ok = n == 0
            elif match.startswith("count:"):
                ok = n == int(match.split(":", 1)[1])
            else:
                ok = False
            results.append({"name": g["name"], "type": kind, "passed": ok, "weight": weight,
                            "scored": True, "detail": "%d match(es)" % n})
        elif kind == "tool_used":
            hits = [t for t in run["tool_uses"] if t["name"] == fm.get("tool")
                    and (not fm.get("input_match") or fm["input_match"] in json.dumps(t["input"]))]
            lo, hi = int(fm.get("min", 1)), fm.get("max")
            ok = len(hits) >= lo and (hi is None or len(hits) <= int(hi))
            scored = fm.get("arm") == "both"
            if fm.get("arm") == "with-only" and run["arm"] == "without":
                continue
            results.append({"name": g["name"], "type": kind, "passed": ok, "weight": weight,
                            "scored": scored, "detail": "%d call(s)" % len(hits)})
        elif kind == "llm":
            llm_criteria.append((g["name"], g["body"], weight))
    verdicts, jcost = judge([(n, b) for n, b, _ in llm_criteria], run["last_message"], judge_model) \
        if run["last_message"] else ({}, 0.0)
    for name, _, weight in llm_criteria:
        v = verdicts.get(name) or {}
        results.append({"name": name, "type": "llm", "passed": str(v.get("verdict", "")).upper() == "PASS",
                        "weight": weight, "scored": True, "detail": v.get("reason", "no verdict")})
    scored = [r for r in results if r["scored"]]
    total = sum(r["weight"] for r in scored)
    score = sum(r["weight"] for r in scored if r["passed"]) / total if total else 0.0
    _, mfind = check_mermaid(run["last_message"])
    m_errors = sum(1 for f in mfind if f.level == "error")
    return {"score": round(score, 3), "graders": results, "judge_cost": jcost,
            "mermaid_blocks": run["last_message"].count("```mermaid"), "mermaid_errors": m_errors}


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--eval-dir", default=os.path.join(REPO, "evals"),
                    help="folder with the eval cases (default: <repo>/evals, outside the plugin)")
    ap.add_argument("--case", help="regex filter on case names")
    ap.add_argument("--runs", type=int, help="override runs per case (default: prompt.md runs)")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--judge-model", default="opus")
    ap.add_argument("--max-cost", type=float, default=60.0, help="stop starting runs above this spend (USD)")
    ap.add_argument("--per-run-budget", type=float, default=4.0)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--arms", default="with,without")
    ap.add_argument("--out", help="results directory")
    args = ap.parse_args()

    plugin = os.path.abspath(args.plugin)
    sys.path.insert(0, os.path.join(plugin, "scripts"))
    from _miniyaml import loads  # noqa: E402
    from check_mermaid import check_text  # noqa: E402

    eval_dir = os.path.abspath(args.eval_dir)
    cases = load_cases(eval_dir, loads, args.case)
    out_dir = args.out or os.path.join(eval_dir, "results",
                                       dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out_dir, exist_ok=True)
    jobs = []
    for c in cases:
        for r in range(args.runs or int(c["fm"].get("runs", 3))):
            for arm in args.arms.split(","):
                jobs.append((c, arm, r))

    def work(job):
        c, arm, r = job
        with LOCK:
            if SPENT[0] >= args.max_cost:
                return None
        run = run_agent(c, arm, plugin, args.model, args.per_run_budget)
        g = grade(c, run, args.judge_model, check_text)
        with LOCK:
            SPENT[0] += run["cost"] + g["judge_cost"]
            spent = SPENT[0]
        rec = {"case": c["name"], "arm": arm, "run": r, "cost": run["cost"], "seconds": run["seconds"],
               "turns": run["turns"], "error": run["is_error"], "timed_out": run["timed_out"],
               "tools": [t["name"] for t in run["tool_uses"]],
               "skills": [t["input"].get("skill") for t in run["tool_uses"] if t["name"] == "Skill"
                          and isinstance(t["input"], dict)], **g}
        base = os.path.join(out_dir, "%s.%s.%d" % (c["name"], arm, r))
        with open(base + ".md", "w", encoding="utf-8") as fh:
            fh.write(run["last_message"])
        with open(base + ".json", "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=2)
        with open(base + ".tools.json", "w", encoding="utf-8") as fh:
            json.dump(run["tool_uses"], fh, indent=2)
        print("[$%.2f] %s %-7s run %d score %.2f mermaid_err %d (%ss)%s" % (
            spent, c["name"], arm, r, g["score"], g["mermaid_errors"], run["seconds"],
            " ERROR" if run["is_error"] else ""), flush=True)
        return rec

    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        records = [r for r in ex.map(work, jobs) if r]
    with open(os.path.join(out_dir, "aggregate-result.json"), "w", encoding="utf-8") as fh:
        json.dump({"model": args.model, "judge_model": args.judge_model, "cost_usd": round(SPENT[0], 2),
                   "records": records}, fh, indent=2)
    print("results:", out_dir, "spent $%.2f" % SPENT[0])


if __name__ == "__main__":
    main()
