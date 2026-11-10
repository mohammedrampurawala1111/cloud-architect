import io
import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import _miniyaml  # noqa: E402
import team_score  # noqa: E402
from _common import InputError  # noqa: E402

SAMPLES = os.path.join(SCRIPTS, "samples")


def team(**over):
    base = {
        "operators": 1, "on_call": False, "platform_team": False,
        "skills": {"containers": 0, "kubernetes": 0, "iac": 0},
        "preference": "balanced",
    }
    skills = over.pop("skills", None)
    base.update(over)
    if skills:
        base["skills"].update(skills)
    return {"team": base}


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = team_score.main(list(args))
    return code, out.getvalue(), err.getvalue()


class BudgetRules(unittest.TestCase):
    def budget(self, doc):
        return team_score.run(doc)["budget"]

    def test_minimum_team_is_one(self):
        self.assertEqual(self.budget(team()), 1)

    def test_skill_worked_example(self):
        # skills/team-fit/SKILL.md output example: 1 + 1 - 0.5 = 1.5 -> 2
        with open(os.path.join(SAMPLES, "team.yaml"), encoding="utf-8") as fh:
            r = team_score.run(_miniyaml.loads(fh.read()))
        self.assertEqual(r["raw_score"], 1.5)
        self.assertEqual(r["budget"], 2)
        self.assertEqual([o["verdict"] for o in r["options"]], ["within", "within", "at_limit"])

    def test_each_factor_adds_one(self):
        self.assertEqual(self.budget(team(operators=2)), 2)
        self.assertEqual(self.budget(team(on_call=True)), 2)
        self.assertEqual(self.budget(team(skills={"containers": 2, "iac": 2})), 2)
        self.assertEqual(self.budget(team(skills={"kubernetes": 2})), 2)
        self.assertEqual(self.budget(team(platform_team=True)), 2)

    def test_containers_and_iac_both_required(self):
        self.assertEqual(self.budget(team(skills={"containers": 3, "iac": 1})), 1)
        self.assertEqual(self.budget(team(skills={"containers": 1, "iac": 3})), 1)

    def test_k8s_and_platform_team_count_once(self):
        self.assertEqual(self.budget(team(platform_team=True, skills={"kubernetes": 3})), 2)

    def test_iac_map_uses_best_tool(self):
        r = team_score.run(team(skills={"containers": 2, "iac": {"terraform": 1, "pulumi": 2}}))
        self.assertEqual(r["budget"], 2)

    def test_preference_rounding_half_up(self):
        # 2 + 0.5 = 2.5 -> 3 (half up, not banker's rounding)
        self.assertEqual(self.budget(team(operators=2, preference="control")), 3)
        # 2 - 0.5 = 1.5 -> 2
        self.assertEqual(self.budget(team(operators=2, preference="managed")), 2)
        # 1 - 0.5 = 0.5 -> 1
        self.assertEqual(self.budget(team(preference="managed")), 1)

    def test_clamped_to_five(self):
        doc = team(operators=6, on_call=True, platform_team=True, preference="control",
                   skills={"containers": 3, "iac": 3, "kubernetes": 3})
        r = team_score.run(doc)
        self.assertEqual(r["raw_score"], 5.5)
        self.assertEqual(r["budget"], 5)

    def test_breakdown_sums_to_raw(self):
        r = team_score.run(team(operators=3, on_call=True, preference="managed"))
        self.assertEqual(sum(b["points"] for b in r["breakdown"]), r["raw_score"])

    def test_missing_fields_are_assumptions(self):
        r = team_score.run({"team": {"skills": {}}})
        self.assertEqual(r["budget"], 1)
        self.assertTrue(any("on_call" in w for w in r["warnings"]))

    def test_builders_used_when_operators_missing(self):
        r = team_score.run({"team": {"builders": 3, "skills": {}}})
        self.assertEqual(r["budget"], 2)
        self.assertTrue(any("builders" in w for w in r["warnings"]))

    def test_bare_team_object_accepted(self):
        self.assertEqual(self.budget({"operators": 2, "skills": {}}), 2)

    def test_bad_values_rejected(self):
        for doc in (team(preference="yolo"), team(on_call="sometimes"),
                    team(skills={"kubernetes": 7}), team(operators=-1)):
            with self.assertRaises(InputError):
                team_score.run(doc)


class OptionVerdicts(unittest.TestCase):
    def verdict(self, budget_doc, option):
        return team_score.run(dict(budget_doc, options=[option]))["options"][0]

    def test_verdict_boundaries(self):
        doc = team(operators=2)  # budget 2
        self.assertEqual(self.verdict(doc, {"complexity": 2})["verdict"], "within")
        self.assertEqual(self.verdict(doc, {"complexity": 3})["verdict"], "at_limit")
        self.assertEqual(self.verdict(doc, {"complexity": 4})["verdict"], "exceeds")

    def test_kubernetes_exceeds_budget_one(self):
        o = self.verdict(team(), {"name": "K8s", "components": [{"class": "managed_kubernetes"}]})
        self.assertEqual((o["complexity"], o["verdict"]), (3, "exceeds"))

    def test_more_than_eight_components_adds_one(self):
        comps = [{"class": "managed_database"}] * 8
        self.assertEqual(self.verdict(team(), {"components": comps})["complexity"], 1)
        comps9 = comps + [{"class": "object_storage"}]
        o = self.verdict(team(), {"components": comps9})
        self.assertEqual((o["complexity"], o["component_penalty"]), (2, 1))

    def test_non_runtime_components_not_counted(self):
        comps = [{"class": "managed_database"}] * 8 + [{"class": "managed_ci_cd", "runtime": False}]
        self.assertEqual(self.verdict(team(), {"components": comps})["complexity"], 1)

    def test_explicit_weight_wins(self):
        o = self.verdict(team(), {"components": [{"class": "managed_database", "weight": 4}]})
        self.assertEqual(o["complexity"], 4)

    def test_unknown_class_suggests(self):
        with self.assertRaises(InputError) as ctx:
            team_score.run(dict(team(), options=[{"components": [{"class": "managed_kubernets"}]}]))
        self.assertIn("managed_kubernetes", str(ctx.exception))


class Cli(unittest.TestCase):
    def test_yaml_and_json_samples_agree(self):
        c1, y, _ = run_cli(os.path.join(SAMPLES, "team.yaml"))
        c2, j, _ = run_cli(os.path.join(SAMPLES, "team.json"))
        self.assertEqual((c1, c2), (0, 0))
        self.assertEqual(json.loads(y), json.loads(j))

    def test_markdown(self):
        code, out, _ = run_cli(os.path.join(SAMPLES, "team.yaml"), "--format", "markdown")
        self.assertEqual(code, 0)
        self.assertIn("**Operational complexity budget: 2 / 5**", out)
        self.assertIn("| C. Kubernetes + GitOps | 3 | At limit |", out)

    def test_invalid_input_exit_2(self):
        code, _, err = run_cli(os.path.join(SAMPLES, "does-not-exist.yaml"))
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_list_classes(self):
        code, out, _ = run_cli("--list-classes")
        self.assertEqual(code, 0)
        self.assertIn("managed_kubernetes", json.loads(out)["3"])


class MiniYaml(unittest.TestCase):
    def test_subset(self):
        doc = _miniyaml.loads(
            "a: 1\nb:\n  c: [x, 'y z']\n  d: { e: true, f: null }\n"
            "list:\n  - one\n  - k: v\n    k2: 2.5\n# comment\ns: \"q # not comment\"\n"
            "same_indent:\n- p\n- q\n")
        self.assertEqual(doc, {
            "a": 1, "b": {"c": ["x", "y z"], "d": {"e": True, "f": None}},
            "list": ["one", {"k": "v", "k2": 2.5}], "s": "q # not comment",
            "same_indent": ["p", "q"]})

    def test_rejects_block_scalars_and_tabs(self):
        with self.assertRaises(_miniyaml.YamlError):
            _miniyaml.loads("a: |\n  text\n")
        with self.assertRaises(_miniyaml.YamlError):
            _miniyaml.loads("a:\n\tb: 1\n")

    def test_bad_indentation(self):
        with self.assertRaises(_miniyaml.YamlError):
            _miniyaml.loads("a: 1\n   b: 2\n")


if __name__ == "__main__":
    unittest.main()


class Evidence(unittest.TestCase):
    def test_default_self_reported(self):
        r = team_score.run(team())
        self.assertTrue(all(b["source"] == "self-reported" for b in r["breakdown"][1:]))
        self.assertIn("Evidence: none; all 5 factors are self-reported.", team_score.to_markdown(r))

    def test_evidence_is_reported_not_scored(self):
        plain = team_score.run(team(operators=2, skills={"kubernetes": 2}))
        doc = team(operators=2, skills={"kubernetes": 2})
        doc["team"]["evidence"] = {"kubernetes": "12 Helm charts in deploy/", "iac": "infra/*.tf"}
        r = team_score.run(doc)
        self.assertEqual(r["budget"], plain["budget"])
        k8s = [b for b in r["breakdown"] if b["factor"].startswith("solid Kubernetes")][0]
        self.assertEqual(k8s["source"], "kubernetes: 12 Helm charts in deploy/")
        md = team_score.to_markdown(r)
        self.assertIn("Evidence: 2 of 5 factors backed", md)
        self.assertIn("the rest self-reported", md)

    def test_unknown_evidence_key(self):
        doc = team()
        doc["team"]["evidence"] = {"rust": "Cargo.toml"}
        with self.assertRaises(InputError):
            team_score.run(doc)
