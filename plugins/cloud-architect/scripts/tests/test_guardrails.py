import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import guardrails  # noqa: E402
from _common import InputError  # noqa: E402

SAMPLES = os.path.join(SCRIPTS, "samples")
ORG = {"name": "Acme", "clouds": ["aws"], "regions": ["eu-central-1"],
       "approved_services": ["ECS on Fargate", "RDS for PostgreSQL"],
       "forbidden_classes": ["self_hosted_database"]}


def opt(*comps, **kw):
    o = {"name": "A", "provider": "aws", "region": "eu-central-1", "components": list(comps)}
    o.update(kw)
    return o


def run(*options, org=None):
    return guardrails.run({"org": dict(org or ORG), "options": list(options)})


def findings(r, i=0):
    return [f["rule"] for c in r["options"][i]["components"] for f in c["findings"]]


class Rules(unittest.TestCase):
    def test_fits(self):
        r = run(opt({"name": "API", "product": "ECS on Fargate", "class": "managed_containers"}))
        self.assertEqual((r["options"][0]["exceptions"], r["options"][0]["verdict"]), (0, "fits guardrails"))
        self.assertIn("Every component fits", guardrails.to_markdown(r))

    def test_name_matching_ignores_case_and_dashes(self):
        r = run(opt({"name": "API", "product": "ecs-on-fargate"}))
        self.assertEqual(findings(r), [])

    def test_unapproved_product(self):
        r = run(opt({"name": "Cluster", "product": "EKS", "class": "managed_kubernetes"}))
        self.assertEqual(findings(r), ["approved services"])
        self.assertEqual(r["options"][0]["verdict"], "needs 1 exception ADR")

    def test_forbidden_class_reported_once(self):
        r = run(opt({"name": "DB", "product": "Postgres on VMs", "class": "self_hosted_database"}))
        self.assertEqual(findings(r), ["forbidden class"])

    def test_region_and_cloud(self):
        r = run(opt({"name": "DB", "product": "RDS for PostgreSQL", "region": "us-east-1"},
                    {"name": "Fn", "product": "ECS on Fargate", "provider": "gcp"}))
        self.assertEqual(findings(r), ["region", "cloud"])
        self.assertEqual(r["options"][0]["exceptions"], 2)

    def test_global_component_skips_region(self):
        org = dict(ORG, approved_services=["CloudFront"])
        r = run(opt({"name": "CDN", "product": "CloudFront", "region": "global", "global": True}), org=org)
        self.assertEqual(findings(r), [])

    def test_missing_region_is_flagged(self):
        r = run({"name": "A", "provider": "aws", "components": [{"name": "API", "product": "ECS on Fargate"}]})
        self.assertEqual(findings(r), ["region"])

    def test_approved_classes(self):
        org = {"approved_classes": ["managed_containers"]}
        r = run(opt({"name": "API", "product": "Anything", "class": "managed_containers"},
                    {"name": "Cache", "product": "Redis", "class": "managed_cache"}), org=org)
        self.assertEqual(findings(r), ["approved services"])


class Validation(unittest.TestCase):
    def test_rejects(self):
        bad = [
            {"org": {}, "options": [opt({"name": "x"})]},
            {"org": {"clouds": "aws"}, "options": [opt({"name": "x"})]},
            {"org": {"forbidden_classes": ["nope"]}, "options": [opt({"name": "x"})]},
            {"org": ORG, "options": []},
            {"org": ORG, "options": [{"name": "A", "components": []}]},
            {"org": ORG, "options": [opt({"name": "x", "class": "nope"})]},
        ]
        for doc in bad:
            with self.assertRaises(InputError, msg=doc):
                guardrails.run(doc)


class Cli(unittest.TestCase):
    def test_samples(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = guardrails.main([os.path.join(SAMPLES, "org.yaml"), "--options",
                                    os.path.join(SAMPLES, "guardrail_options.yaml")])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn("| A. Managed containers | 0 | fits guardrails |", out.getvalue())
        self.assertIn("| B. Kubernetes | 3 | needs 3 exception ADRs |", out.getvalue())

    def test_invalid_exit_2(self):
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = guardrails.main([os.path.join(SAMPLES, "team.yaml")])
        self.assertEqual(code, 2)
