#!/usr/bin/env python3
"""Basic syntax checks for ```mermaid blocks in a Markdown file (cloud-architect).

Catches the mistakes that most often stop a diagram from rendering:
  - missing or unknown diagram header (flowchart LR, sequenceDiagram, C4Context...)
  - invalid flowchart direction
  - unbalanced (), [], {} outside quoted strings
  - parentheses/brackets inside an unquoted node label: A[Foo (bar)] -> A["Foo (bar)"]
  - subgraph/end mismatch in flowcharts; unclosed alt/opt/loop/par/... blocks in
    sequence diagrams
  - a flowchart node id of "end" (reserved word; breaks the parser)
  - empty blocks and unterminated ``` fences

It is a lint, not a full Mermaid parser: a clean result means "no known basic
error", not a guaranteed render. Standard library only; no network access.
Exit status: 0 no errors, 1 errors found, 2 cannot read input.
"""

import argparse
import json
import os
import re
import sys

DIAGRAM_TYPES = {
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "classDiagram-v2",
    "stateDiagram", "stateDiagram-v2", "erDiagram", "journey", "gantt", "pie",
    "quadrantChart", "requirementDiagram", "gitGraph", "mindmap", "timeline",
    "sankey-beta", "sankey", "xychart-beta", "xychart", "block-beta", "block",
    "packet-beta", "packet", "kanban", "architecture-beta", "radar-beta",
    "treemap-beta", "zenuml",
    "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
}
FLOW_DIRECTIONS = {"TB", "TD", "BT", "RL", "LR"}
FLOW_SKIP_PREFIXES = ("classDef ", "class ", "style ", "linkStyle ", "click ", "direction ",
                      "accTitle", "accDescr")
# Longest openers first. Value: acceptable closers.
SHAPES = [
    ("(((", (")))",)), ("((", ("))",)), ("([", ("])",)), ("[(", (")]",)), ("[[", ("]]",)),
    ("[/", ("/]", "\\]")), ("[\\", ("\\]", "/]")), ("{{", ("}}",)),
    ("(", (")",)), ("[", ("]",)), ("{", ("}",)),
]
SEQ_OPENERS = ("alt", "opt", "loop", "par", "critical", "break", "rect", "box")
PAIRS = {")": "(", "]": "[", "}": "{"}
FENCE = re.compile(r"^(\s*)(```+|~~~+)\s*(\S*)")
ID_CHAR = re.compile(r"[A-Za-z0-9_\-]")


class Finding:
    def __init__(self, level, line, block, message):
        self.level, self.line, self.block, self.message = level, line, block, message

    def as_dict(self):
        return {"level": self.level, "line": self.line, "block": self.block, "message": self.message}


def extract_blocks(text):
    """Yield (block_no, first_content_line_no, [lines]) and fence problems."""
    lines = text.splitlines()
    blocks, problems = [], []
    i, n = 0, len(lines)
    while i < n:
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        fence, lang = m.group(2), m.group(3).lower()
        start = i + 1
        j = start
        while j < n:
            m2 = FENCE.match(lines[j])
            if m2 and m2.group(2)[0] == fence[0] and len(m2.group(2)) >= len(fence) and not m2.group(3):
                break
            j += 1
        if lang == "mermaid":
            if j >= n:
                problems.append((i + 1, "unterminated ```mermaid fence"))
            blocks.append((len(blocks) + 1, start + 1, lines[start:j]))
        i = j + 1
    return blocks, problems


def strip_quotes(s):
    """Replace double-quoted spans with placeholders so brackets inside are ignored."""
    return re.sub(r'"[^"]*"', '""', s)


def balance_errors(s):
    stack = []
    for ch in strip_quotes(s):
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != PAIRS[ch]:
                return "unbalanced '%s'" % ch
            stack.pop()
    if stack:
        return "unclosed '%s'" % stack[-1]
    return None


def header_of(lines):
    """Return (index, header_line) skipping blank lines, %% comments, %%{init}%% and front matter."""
    i = 0
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    while i < len(lines):
        s = lines[i].strip()
        if s and not s.startswith("%%"):
            return i, s
        i += 1
    return None, None


def check_flow_line(line):
    """Return a list of messages for one flowchart statement."""
    msgs = []
    s = line
    out = []  # the line with node labels and edge labels removed, for the balance check
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch == '"':
            j = s.find('"', i + 1)
            if j == -1:
                msgs.append("unterminated double quote")
                return msgs
            i = j + 1
            continue
        if ch == "|":  # edge label |text|
            j = s.find("|", i + 1)
            if j == -1:
                msgs.append("unterminated edge label '|'")
                return msgs
            i = j + 1
            continue
        prev_is_id = i > 0 and ID_CHAR.match(s[i - 1]) is not None
        if prev_is_id and ch == ">" and not s[i - 1] in "-=":
            opener, closers = ">", ("]",)
        elif prev_is_id and ch in "([{":
            opener, closers = next((o, c) for o, c in SHAPES if s.startswith(o, i))
        else:
            out.append(ch)
            i += 1
            continue
        node_id = re.search(r"([A-Za-z0-9_\-]+)$", s[:i]).group(1)
        if node_id == "end":
            msgs.append("node id 'end' is reserved in flowcharts; rename it (e.g. end_node)")
        k = i + len(opener)
        if k < n and s[k] == '"':
            q = s.find('"', k + 1)
            if q == -1:
                msgs.append("unterminated quoted label for node '%s'" % node_id)
                return msgs
            rest = s[q + 1:]
            closer = next((c for c in closers if rest.startswith(c)), None)
            if closer is None:
                msgs.append("node '%s': expected '%s' after quoted label" % (node_id, closers[0]))
                return msgs
            i = q + 1 + len(closer)
            continue
        # unquoted label: up to the first acceptable closer
        positions = [(s.find(c, k), c) for c in closers if s.find(c, k) != -1]
        if not positions:
            msgs.append("node '%s': '%s' is never closed (expected '%s')" % (node_id, opener, closers[0]))
            return msgs
        end, closer = min(positions)
        label = s[k:end]
        bad = sorted(set(re.findall(r"[()\[\]{}]", label)))
        if bad:
            msgs.append("node '%s': unquoted label %r contains %s; wrap the label in double quotes"
                        % (node_id, label.strip(), " ".join(bad)))
        i = end + len(closer)
    err = balance_errors("".join(out))
    if err:
        msgs.append(err)
    return msgs


def check_block(block_no, first_line, lines):
    f = []

    def add(level, idx, msg):
        f.append(Finding(level, first_line + idx, block_no, msg))

    hidx, header = header_of(lines)
    if header is None:
        add("error", 0, "empty mermaid block")
        return f
    parts = header.split()
    kind = parts[0].rstrip(":")
    if kind not in DIAGRAM_TYPES:
        add("error", hidx, "unknown or missing diagram header %r (e.g. 'flowchart LR', 'sequenceDiagram')" % header)
        return f

    if kind in ("flowchart", "graph"):
        if len(parts) > 1 and parts[1] not in FLOW_DIRECTIONS:
            add("error", hidx, "invalid flowchart direction %r (use TB, TD, BT, RL or LR)" % parts[1])
        depth = 0
        for idx in range(hidx + 1, len(lines)):
            raw = lines[idx].strip()
            if not raw or raw.startswith("%%"):
                continue
            if raw.startswith(FLOW_SKIP_PREFIXES):
                continue
            if raw == "end":
                depth -= 1
                if depth < 0:
                    add("error", idx, "'end' without a matching 'subgraph'")
                    depth = 0
                continue
            stmt = raw
            if raw.startswith("subgraph"):
                depth += 1
                stmt = raw[len("subgraph"):].strip()
                if not stmt:
                    add("error", idx, "subgraph needs an id or title")
                    continue
            for stmt_part in [p for p in stmt.split(";") if p.strip()]:
                for msg in check_flow_line(stmt_part.strip()):
                    add("error", idx, msg)
        if depth > 0:
            add("error", len(lines) - 1, "%d subgraph(s) not closed with 'end'" % depth)

    elif kind == "sequenceDiagram":
        depth = 0
        for idx in range(hidx + 1, len(lines)):
            raw = lines[idx].strip()
            if not raw or raw.startswith("%%"):
                continue
            word = raw.split()[0]
            if word in SEQ_OPENERS:
                depth += 1
            elif word == "end":
                depth -= 1
                if depth < 0:
                    add("error", idx, "'end' without a matching alt/opt/loop/par/critical/break/rect/box")
                    depth = 0
            elif "->" in raw or "--" in raw:
                if ":" not in raw and not raw.startswith(("participant", "actor", "note", "Note", "activate", "deactivate", "autonumber", "create", "destroy")):
                    add("warning", idx, "message without ':' text; Mermaid requires 'A->>B: text'")
        if depth > 0:
            add("error", len(lines) - 1, "%d block(s) not closed with 'end'" % depth)

    elif kind.startswith("C4"):
        for idx in range(hidx + 1, len(lines)):
            raw = lines[idx].strip()
            if not raw or raw.startswith("%%") or raw in ("}",) or raw.endswith("{"):
                continue
            err = balance_errors(raw)
            if err:
                add("error", idx, err)
        opens = sum(l.count("{") for l in (strip_quotes(x) for x in lines[hidx + 1:]))
        closes = sum(l.count("}") for l in (strip_quotes(x) for x in lines[hidx + 1:]))
        if opens != closes:
            add("error", len(lines) - 1, "boundary braces unbalanced ({ %d vs } %d)" % (opens, closes))

    else:
        body = "\n".join(lines[hidx + 1:])
        err = balance_errors(body)
        if err and kind in ("classDiagram", "classDiagram-v2", "erDiagram", "stateDiagram", "stateDiagram-v2"):
            add("warning", hidx, "brackets look unbalanced in this %s (%s)" % (kind, err))
    return f


def check_text(text):
    blocks, problems = extract_blocks(text)
    findings = [Finding("error", ln, None, msg) for ln, msg in problems]
    for block_no, first_line, lines in blocks:
        findings.extend(check_block(block_no, first_line, lines))
    return len(blocks), findings


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check_mermaid.py",
        description="Lint ```mermaid blocks in Markdown files for basic syntax errors.",
        epilog="Example: python3 check_mermaid.py docs/architecture/shop/diagrams.md\n"
               "Exit status: 0 no errors, 1 errors found, 2 cannot read input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("files", nargs="+", help="Markdown files to check ('-' reads stdin)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--require-blocks", action="store_true", help="error if a file has no mermaid blocks")
    args = ap.parse_args(argv)

    report, errors = [], 0
    for path in args.files:
        try:
            if path == "-":
                text = sys.stdin.read()
            else:
                with open(path, "r", encoding="utf-8") as fh:
                    text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            sys.stderr.write("%s: error: cannot read %s: %s\n" % (ap.prog, path, exc))
            return 2
        count, findings = check_text(text)
        if args.require_blocks and count == 0:
            findings.append(Finding("error", 1, None, "no ```mermaid blocks found"))
        if args.strict:
            for fd in findings:
                fd.level = "error"
        errors += sum(1 for fd in findings if fd.level == "error")
        report.append({"file": path, "blocks": count, "findings": [fd.as_dict() for fd in findings]})

    if args.format == "json":
        json.dump({"ok": errors == 0, "errors": errors, "files": report}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for r in report:
            for fd in r["findings"]:
                where = "%s:%d" % (r["file"], fd["line"])
                blk = " (block %d)" % fd["block"] if fd["block"] else ""
                sys.stdout.write("%s: %s%s: %s\n" % (where, fd["level"], blk, fd["message"]))
            n_err = sum(1 for fd in r["findings"] if fd["level"] == "error")
            n_warn = len(r["findings"]) - n_err
            sys.stdout.write("%s: %d mermaid block(s), %d error(s), %d warning(s)\n"
                             % (os.path.basename(r["file"]) if r["file"] != "-" else "stdin",
                                r["blocks"], n_err, n_warn))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
