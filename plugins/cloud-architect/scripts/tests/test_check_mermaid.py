import io
import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import check_mermaid as cm  # noqa: E402

SAMPLES = os.path.join(SCRIPTS, "samples")


def md(body):
    return "# t\n\n```mermaid\n" + body.strip("\n") + "\n```\n"


def errors(body):
    _, findings = cm.check_text(md(body))
    return [f.message for f in findings if f.level == "error"]


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cm.main(list(args))
    return code, out.getvalue(), err.getvalue()


class Flowcharts(unittest.TestCase):
    def test_valid_shapes(self):
        body = """
flowchart LR
  a([Actor]) --> b[Service<br/>containers]
  b --> c[(DB)]
  b -.->|async event| d[[Queue]]
  b --> e{{External}}
  b --> f{Decision}
  b --> g((Circle))
  b --> h[/Parallelogram/]
  b --> i>Flag]
  b --> j["Quoted (ok) [also ok]"]
  b == bold ==> k
"""
        self.assertEqual(errors(body), [])

    def test_unquoted_parentheses(self):
        errs = errors("flowchart LR\n  api[API (Cloud Run)] --> db")
        self.assertEqual(len(errs), 1)
        self.assertIn("double quotes", errs[0])

    def test_unquoted_parentheses_in_db_shape(self):
        errs = errors("flowchart LR\n  db[(Primary DB (EU))]")
        self.assertTrue(any("unquoted label" in e for e in errs))

    def test_unclosed_shape(self):
        self.assertTrue(errors("flowchart LR\n  a[Open --> b"))

    def test_unbalanced_outside_labels(self):
        self.assertTrue(errors("flowchart LR\n  a --> b)"))

    def test_direction(self):
        self.assertIn("invalid flowchart direction", errors("flowchart XY\n  a --> b")[0])
        self.assertEqual(errors("graph TD\n  a --> b"), [])
        self.assertEqual(errors("flowchart\n  a --> b"), [])

    def test_subgraph_end_pairing(self):
        self.assertTrue(errors("flowchart TB\n  subgraph x[X]\n    a\n"))
        self.assertTrue(errors("flowchart TB\n  a\n  end\n"))
        self.assertEqual(errors("flowchart TB\n  subgraph x[X]\n    direction LR\n    a\n  end\n"), [])

    def test_reserved_end_id(self):
        self.assertTrue(any("reserved" in e for e in errors("flowchart LR\n  a --> end[Done]")))

    def test_style_lines_ignored(self):
        body = "flowchart LR\n  a --> b\n  classDef locked fill:#fee,stroke:#c00\n  class a locked\n  style b fill:#eef\n"
        self.assertEqual(errors(body), [])

    def test_unterminated_quote(self):
        self.assertTrue(errors('flowchart LR\n  a["oops] --> b'))


class OtherDiagrams(unittest.TestCase):
    def test_header_required(self):
        self.assertIn("unknown or missing diagram header", errors("a --> b")[0])
        self.assertTrue(errors("flowhcart LR\n a-->b"))

    def test_init_directive_and_comments_skipped(self):
        body = "%%{init: {'theme': 'neutral'}}%%\n%% comment\nflowchart LR\n  a --> b"
        self.assertEqual(errors(body), [])

    def test_front_matter_skipped(self):
        self.assertEqual(errors("---\ntitle: X\n---\nflowchart LR\n  a --> b"), [])

    def test_sequence_blocks(self):
        ok = "sequenceDiagram\n  A->>B: call (x)\n  alt ok\n    B-->>A: yes\n  else no\n    B-->>A: no\n  end"
        self.assertEqual(errors(ok), [])
        self.assertTrue(errors("sequenceDiagram\n  loop retry\n    A->>B: x"))
        self.assertTrue(errors("sequenceDiagram\n  A->>B: x\n  end"))

    def test_c4(self):
        ok = 'C4Context\n  Person(u, "User (web)")\n  System_Boundary(b, "B") {\n    System(s, "S")\n  }\n  Rel(u, s, "Uses")'
        self.assertEqual(errors(ok), [])
        self.assertTrue(errors('C4Context\n  Person(u, "User"'))

    def test_empty_block(self):
        self.assertIn("empty", errors("\n")[0])

    def test_unterminated_fence(self):
        _, findings = cm.check_text("```mermaid\nflowchart LR\n  a --> b\n")
        self.assertTrue(any("unterminated" in f.message for f in findings))

    def test_non_mermaid_blocks_ignored(self):
        count, findings = cm.check_text("```python\nprint((1)\n```\n")
        self.assertEqual((count, findings), (0, []))


class Cli(unittest.TestCase):
    def test_valid_sample_passes(self):
        code, out, _ = run_cli(os.path.join(SAMPLES, "diagrams.md"))
        self.assertEqual(code, 0, out)
        self.assertIn("3 mermaid block(s), 0 error(s)", out)

    def test_bad_sample_fails_with_line_numbers(self):
        code, out, _ = run_cli(os.path.join(SAMPLES, "diagrams_bad.md"), "--format", "json")
        self.assertEqual(code, 1)
        res = json.loads(out)
        lines = sorted({f["line"] for f in res["files"][0]["findings"]})
        self.assertEqual(lines, [5, 6, 11, 16, 23, 30])
        self.assertEqual(res["errors"], 7)

    def test_require_blocks(self):
        code, _, _ = run_cli(os.path.join(SCRIPTS, "README.md"), "--require-blocks")
        self.assertEqual(code, 1)

    def test_missing_file_exit_2(self):
        code, _, err = run_cli(os.path.join(SAMPLES, "nope.md"))
        self.assertEqual(code, 2)
        self.assertIn("cannot read", err)


if __name__ == "__main__":
    unittest.main()
