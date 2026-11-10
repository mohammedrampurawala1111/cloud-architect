import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import plan  # noqa: E402
from _common import InputError  # noqa: E402

SAMPLE = os.path.join(SCRIPTS, "samples", "plan.yaml")
ORG = os.path.join(SCRIPTS, "samples", "org.yaml")
TEAM = {"builders": 2, "operators": 1, "on_call": False, "skills": {"containers": 1}}


def doc(**kw):
    d = {"team": dict(TEAM), "options": [{"name": "A", "provider": "aws", "region": "eu-central-1",
                                          "components": [{"name": "API", "class": "managed_containers",
                                                          "product": "ECS on Fargate"}]}]}
    d.update(kw)
    return d


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = plan.main(list(args))
    return code, out.getvalue(), err.getvalue()


class Plan(unittest.TestCase):
    def test_sections_without_org(self):
        r = plan.run(doc())
        self.assertIsNone(r["guardrails"])
        md = plan.to_markdown(r)
        self.assertIn("### Team fit", md)
        self.assertNotIn("### Cost", md)
        self.assertNotIn("### Org guardrails", md)

    def test_inline_org(self):
        r = plan.run(doc(org={"clouds": ["azure"]}))
        self.assertEqual(r["guardrails"]["options"][0]["exceptions"], 1)

    def test_same_results_as_scripts(self):
        import team_score
        d = doc()
        r = plan.run(d)
        self.assertEqual(r["team_fit"], team_score.run(d))
        self.assertEqual(set(r), {"team_fit", "guardrails"})

    def test_extra_cost_keys_are_ignored(self):
        d = doc()
        d["options"][0]["components"][0]["monthly_cost"] = 100
        self.assertEqual(plan.run(d)["team_fit"], plan.run(doc())["team_fit"])

    def test_errors_name_the_step(self):
        bad = doc()
        bad["options"][0]["components"][0]["class"] = "nope"
        with self.assertRaisesRegex(InputError, "^team fit:"):
            plan.run(bad)
        with self.assertRaisesRegex(InputError, "^team fit:"):
            plan.run({"options": doc()["options"]})
        with self.assertRaises(InputError):
            plan.run({"team": TEAM})

    def test_sample_cli_with_org_file(self):
        code, out, _ = run_cli(SAMPLE, "--org", ORG)
        self.assertEqual(code, 0)
        self.assertIn("needs 1 exception ADR", out)
        self.assertIn("Operational complexity budget: 2 / 5", out)


if __name__ == "__main__":
    unittest.main()
