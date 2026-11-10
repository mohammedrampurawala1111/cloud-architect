import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import inventory  # noqa: E402
from _common import InputError  # noqa: E402


def make(tree):
    root = tempfile.mkdtemp(prefix="inv-")
    for rel, text in tree.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
    return root


NODE = {
    "package.json": json.dumps({"dependencies": {"express": "4", "pg": "8", "@aws-sdk/client-sqs": "3",
                                                 "ioredis": "5", "stripe": "1"},
                                "devDependencies": {"jest": "29"}}),
    "src/server.ts": "import express from 'express'",
    "src/app/index.ts": "",
    "Dockerfile": "FROM node:22-alpine AS build\nFROM gcr.io/distroless/nodejs22\n",
    "infra/main.tf": 'resource "aws_db_instance" "db" {}\nresource "aws_sqs_queue" "q" {}\nresource "aws_sqs_queue" "dlq" {}\n',
    "deploy/chart/Chart.yaml": "name: api\n",
    "deploy/k8s/deploy.yaml": "apiVersion: apps/v1\nkind: Deployment\n---\napiVersion: v1\nkind: Service\n",
    ".github/workflows/ci.yml": "on: push\n",
    "db/migrations/001_init.sql": "create table t (id int);",
    "api/openapi.yaml": "openapi: 3.0.0\n",
    "node_modules/express/package.json": json.dumps({"dependencies": {"mongodb": "6"}}),
}


class Scan(unittest.TestCase):
    def setUp(self):
        self.root = make(NODE)
        self.r = inventory.scan(self.root)

    def test_stack_by_role(self):
        st = self.r["stack"]
        self.assertIn("Express", st["web"])
        self.assertIn("PostgreSQL", st["data store"])
        self.assertIn("SQS", st["messaging"])
        self.assertIn("Redis", st["cache"])
        self.assertIn("Stripe (payments)", st["integrations"])
        self.assertIn("AWS", st["cloud sdk"])
        self.assertIn("Jest", st["testing"])

    def test_skips_dependency_folders(self):
        self.assertNotIn("MongoDB", self.r["stack"].get("data store", {}))

    def test_platform_files(self):
        self.assertEqual(self.r["iac"]["terraform_resources"], {"aws_sqs_queue": 2, "aws_db_instance": 1})
        self.assertEqual(self.r["kubernetes"]["kinds"], {"Deployment": 1, "Service": 1})
        self.assertEqual(self.r["kubernetes"]["helm_charts"], ["deploy/chart/Chart.yaml"])
        self.assertEqual(self.r["containers"]["images"], {"node:22-alpine": 1, "gcr.io/distroless/nodejs22": 1})
        self.assertEqual(self.r["ci_cd"], [{"file": ".github/workflows/ci.yml", "tool": "GitHub Actions"}])
        self.assertEqual(self.r["migrations"], ["db/migrations/"])
        self.assertEqual(self.r["api_contracts"], [{"file": "api/openapi.yaml", "type": "OpenAPI"}])
        self.assertIn("src/server.ts", self.r["entry_points"])

    def test_evidence_and_markdown(self):
        ev = inventory.evidence_lines(self.r)
        self.assertEqual(ev["containers"], "1 Dockerfile in the repo")
        self.assertEqual(ev["kubernetes"], "1 Kubernetes manifest and 1 Helm chart in the repo")
        self.assertEqual(ev["iac"], "1 Terraform file in the repo")
        for v in ev.values():
            self.assertNotRegex(v, r"[:\"'{}\[\]]")   # safe as team.evidence values
        md = inventory.to_markdown(self.r)
        self.assertIn("**Web framework:** Express", md)
        self.assertIn("Team-profile evidence:", md)

    def test_same_tree_same_result(self):
        self.assertEqual(inventory.scan(self.root), self.r)


class Manifests(unittest.TestCase):
    def deps(self, name, text):
        return inventory.deps_from(name, name, text)

    def test_python(self):
        self.assertEqual(self.deps("requirements.txt", "Django==5.1\n# c\npsycopg[binary]>=3\n-r other.txt\n"),
                         ["Django", "psycopg"])
        self.assertIn("fastapi", self.deps("pyproject.toml", 'dependencies = [\n  "fastapi>=0.115",\n]\n'))

    def test_go_java_dotnet(self):
        self.assertIn("github.com/gin-gonic/gin", self.deps("go.mod", "require (\n\tgithub.com/gin-gonic/gin v1.10.0\n)\n"))
        pom = "<dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId></dependency>"
        self.assertIn("org.postgresql:postgresql", self.deps("pom.xml", pom))
        self.assertEqual(self.deps("Api.csproj", '<PackageReference Include="Npgsql" Version="8" />'), ["Npgsql"])
        self.assertIn(("data store", "PostgreSQL"), inventory.match_sig("Npgsql"))

    def test_bad_json_is_ignored(self):
        self.assertEqual(self.deps("package.json", "{not json"), [])


class Cli(unittest.TestCase):
    def test_empty_and_missing(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(inventory.main([tempfile.mkdtemp()]), 0)
        self.assertIn("Nothing recognisable found", out.getvalue())
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(inventory.main(["/nonexistent/path"]), 2)

    def test_json_has_evidence(self):
        out = io.StringIO()
        with redirect_stdout(out):
            inventory.main([make(NODE), "--format", "json"])
        self.assertIn("team_evidence", json.loads(out.getvalue()))
