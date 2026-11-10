#!/usr/bin/env python3
"""Read-only inventory of an existing codebase (cloud-architect).

Scans a repository and reports what the system is built from, with the files
that show it: languages, frameworks and libraries by role (web, data store,
ORM, cache, messaging, cloud SDK, auth, observability), API contracts, database
migrations, containers, Kubernetes, IaC resources and CI/CD. The same tree
always gives the same inventory.

Read-only: it opens text files under the root (skipping dependency, build and
VCS folders and files over 256 KiB), writes only to stdout, and makes no network calls. Standard library only.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import InputError, fail  # noqa: E402

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", ".venv", "venv", "env", "dist", "build",
             "target", "out", "bin", "obj", "__pycache__", ".terraform", ".next", ".nuxt", ".gradle",
             ".idea", ".vscode", "coverage", ".pytest_cache", ".mypy_cache", ".tox"}
MAX_BYTES = 256 * 1024
EXT_LANG = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
            ".jsx": "JavaScript", ".mjs": "JavaScript", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
            ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".rs": "Rust", ".scala": "Scala",
            ".swift": "Swift", ".ex": "Elixir", ".exs": "Elixir"}

# Dependency name (lower-case, exact or prefix ending in '*') -> (role, label).
SIGNATURES = [
    # web frameworks
    ("express", "web", "Express"), ("fastify", "web", "Fastify"), ("@nestjs/core", "web", "NestJS"),
    ("next", "web", "Next.js"), ("koa", "web", "Koa"), ("hono", "web", "Hono"),
    ("django", "web", "Django"), ("flask", "web", "Flask"), ("fastapi", "web", "FastAPI"),
    ("spring-boot-starter-web", "web", "Spring Boot"), ("spring-boot-starter-webflux", "web", "Spring WebFlux"),
    ("github.com/gin-gonic/gin", "web", "Gin"), ("github.com/labstack/echo*", "web", "Echo"),
    ("github.com/gofiber/fiber*", "web", "Fiber"), ("microsoft.aspnetcore*", "web", "ASP.NET Core"),
    ("rails", "web", "Rails"), ("laravel/framework", "web", "Laravel"),
    # data stores (drivers)
    ("pg", "data store", "PostgreSQL"), ("postgres", "data store", "PostgreSQL"),
    ("psycopg*", "data store", "PostgreSQL"), ("asyncpg", "data store", "PostgreSQL"),
    ("github.com/jackc/pgx*", "data store", "PostgreSQL"), ("org.postgresql:postgresql", "data store", "PostgreSQL"),
    ("postgresql", "data store", "PostgreSQL"), ("npgsql*", "data store", "PostgreSQL"),
    ("mysql", "data store", "MySQL"), ("mysql2", "data store", "MySQL"), ("pymysql", "data store", "MySQL"),
    ("mongodb", "data store", "MongoDB"), ("mongoose", "data store", "MongoDB"), ("pymongo", "data store", "MongoDB"),
    ("@aws-sdk/client-dynamodb", "data store", "DynamoDB"), ("@aws-sdk/lib-dynamodb", "data store", "DynamoDB"),
    ("@google-cloud/firestore", "data store", "Firestore"), ("@azure/cosmos", "data store", "Cosmos DB"),
    ("cx_oracle", "data store", "Oracle"), ("oracledb", "data store", "Oracle"),
    ("com.oracle.database.jdbc:ojdbc*", "data store", "Oracle"), ("ojdbc*", "data store", "Oracle"),
    ("@elastic/elasticsearch", "data store", "Elasticsearch"), ("elasticsearch", "data store", "Elasticsearch"),
    ("@opensearch-project/opensearch", "data store", "OpenSearch"),
    # ORMs
    ("prisma", "orm", "Prisma"), ("@prisma/client", "orm", "Prisma"), ("typeorm", "orm", "TypeORM"),
    ("sequelize", "orm", "Sequelize"), ("drizzle-orm", "orm", "Drizzle"), ("knex", "orm", "Knex"),
    ("sqlalchemy", "orm", "SQLAlchemy"), ("alembic", "orm", "Alembic migrations"),
    ("spring-boot-starter-data-jpa", "orm", "JPA / Hibernate"), ("hibernate-core", "orm", "Hibernate"),
    ("microsoft.entityframeworkcore*", "orm", "Entity Framework Core"), ("gorm.io/gorm", "orm", "GORM"),
    # cache
    ("redis", "cache", "Redis"), ("ioredis", "cache", "Redis"), ("github.com/redis/go-redis*", "cache", "Redis"),
    ("memcached", "cache", "Memcached"),
    # messaging
    ("@aws-sdk/client-sqs", "messaging", "SQS"), ("@aws-sdk/client-sns", "messaging", "SNS"),
    ("@aws-sdk/client-eventbridge", "messaging", "EventBridge"), ("@aws-sdk/client-kinesis", "messaging", "Kinesis"),
    ("kafkajs", "messaging", "Kafka"), ("confluent-kafka", "messaging", "Kafka"), ("kafka-python", "messaging", "Kafka"),
    ("spring-kafka", "messaging", "Kafka"), ("github.com/segmentio/kafka-go", "messaging", "Kafka"),
    ("amqplib", "messaging", "RabbitMQ"), ("pika", "messaging", "RabbitMQ"),
    ("spring-boot-starter-amqp", "messaging", "RabbitMQ"), ("bullmq", "messaging", "BullMQ (Redis)"),
    ("bull", "messaging", "Bull (Redis)"), ("celery", "messaging", "Celery"),
    ("@google-cloud/pubsub", "messaging", "Pub/Sub"), ("@azure/service-bus", "messaging", "Azure Service Bus"),
    ("nats", "messaging", "NATS"),
    # cloud SDKs
    ("@aws-sdk/*", "cloud sdk", "AWS"), ("aws-sdk", "cloud sdk", "AWS"), ("boto3", "cloud sdk", "AWS"),
    ("github.com/aws/aws-sdk-go*", "cloud sdk", "AWS"), ("software.amazon.awssdk*", "cloud sdk", "AWS"),
    ("@azure/*", "cloud sdk", "Azure"), ("azure-*", "cloud sdk", "Azure"),
    ("@google-cloud/*", "cloud sdk", "GCP"), ("google-cloud-*", "cloud sdk", "GCP"),
    ("cloud.google.com/go*", "cloud sdk", "GCP"),
    # auth
    ("passport", "auth", "Passport"), ("next-auth", "auth", "NextAuth"), ("jsonwebtoken", "auth", "JWT"),
    ("jose", "auth", "JWT (jose)"), ("pyjwt", "auth", "JWT"), ("auth0", "auth", "Auth0"),
    ("@auth0/*", "auth", "Auth0"), ("@clerk/*", "auth", "Clerk"), ("keycloak*", "auth", "Keycloak"),
    ("spring-boot-starter-security", "auth", "Spring Security"),
    ("spring-boot-starter-oauth2-resource-server", "auth", "OAuth2 resource server"),
    ("@aws-sdk/client-cognito-identity-provider", "auth", "Cognito"), ("amazon-cognito-identity-js", "auth", "Cognito"),
    # observability
    ("@opentelemetry/*", "observability", "OpenTelemetry"), ("opentelemetry-*", "observability", "OpenTelemetry"),
    ("dd-trace", "observability", "Datadog"), ("ddtrace", "observability", "Datadog"),
    ("prom-client", "observability", "Prometheus"), ("prometheus-client", "observability", "Prometheus"),
    ("prometheus_client", "observability", "Prometheus"), ("@sentry/*", "observability", "Sentry"),
    ("sentry-sdk", "observability", "Sentry"), ("newrelic", "observability", "New Relic"),
    ("pino", "observability", "Pino logging"), ("winston", "observability", "Winston logging"),
    # object storage
    ("@aws-sdk/client-s3", "object storage", "S3"), ("@google-cloud/storage", "object storage", "Cloud Storage"),
    ("@azure/storage-blob", "object storage", "Azure Blob Storage"), ("minio", "object storage", "MinIO"),
    # third-party integrations
    ("@aws-sdk/client-ses", "integrations", "SES (email)"), ("@aws-sdk/client-sesv2", "integrations", "SES (email)"),
    ("@sendgrid/mail", "integrations", "SendGrid (email)"), ("nodemailer", "integrations", "SMTP email"),
    ("postmark", "integrations", "Postmark (email)"), ("twilio", "integrations", "Twilio (SMS/voice)"),
    ("stripe", "integrations", "Stripe (payments)"), ("@slack/web-api", "integrations", "Slack"),
    ("@aws-sdk/client-pinpoint-sms-voice-v2", "integrations", "AWS End User Messaging (SMS)"),
    # testing
    ("jest", "testing", "Jest"), ("vitest", "testing", "Vitest"), ("mocha", "testing", "Mocha"),
    ("pytest", "testing", "pytest"), ("junit-jupiter*", "testing", "JUnit"), ("testcontainers*", "testing", "Testcontainers"),
]
ROLE_ORDER = ["web", "data store", "orm", "cache", "messaging", "object storage", "cloud sdk", "auth",
              "integrations", "observability", "testing"]
ROLE_TITLES = {"web": "Web framework", "data store": "Data stores", "orm": "ORM / migrations", "cache": "Cache",
               "messaging": "Messaging / jobs", "object storage": "Object storage", "cloud sdk": "Cloud SDKs",
               "auth": "Auth", "integrations": "Third-party integrations",
               "observability": "Observability", "testing": "Testing"}
CI_FILES = {".gitlab-ci.yml": "GitLab CI", "azure-pipelines.yml": "Azure Pipelines", "Jenkinsfile": "Jenkins",
            "bitbucket-pipelines.yml": "Bitbucket Pipelines", ".circleci/config.yml": "CircleCI"}


def match_sig(dep):
    d = dep.lower().strip()
    out = []
    for pat, role, label in SIGNATURES:
        if pat.endswith("*"):
            if d.startswith(pat[:-1]):
                out.append((role, label))
        elif d == pat:
            out.append((role, label))
    return out


def read(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def deps_from(name, rel, text):
    """Return dependency names declared in a manifest file."""
    deps = []
    if name == "package.json":
        try:
            pj = json.loads(text)
        except ValueError:
            return []
        for k in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            if isinstance(pj.get(k), dict):
                deps += list(pj[k])
    elif name.startswith("requirements") and name.endswith(".txt"):
        for line in text.splitlines():
            line = line.split("#")[0].strip()
            m = re.match(r"([A-Za-z0-9_.\-\[\]]+)", line)
            if m and not line.startswith("-"):
                deps.append(re.sub(r"\[.*\]", "", m.group(1)))
    elif name == "pyproject.toml":
        for m in re.finditer(r'^\s*"([A-Za-z0-9_.\-]+)(?:\[[^\]]*\])?\s*[<>=~!;"]', text, re.M):
            deps.append(m.group(1))
        for m in re.finditer(r'^([A-Za-z0-9_.\-]+)\s*=\s*["{]', text, re.M):
            deps.append(m.group(1))
    elif name == "go.mod":
        for m in re.finditer(r"^\s*(?:require\s+)?([a-z0-9.\-]+\.[a-z]+/[^\s]+)\s+v", text, re.M):
            deps.append(m.group(1))
    elif name == "pom.xml":
        for g, a in re.findall(r"<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>", text):
            deps += [a, "%s:%s" % (g, a)]
    elif name in ("build.gradle", "build.gradle.kts"):
        for m in re.finditer(r"""['"]([A-Za-z0-9_.\-]+):([A-Za-z0-9_.\-]+)(?::[^'"]*)?['"]""", text):
            deps += [m.group(2), "%s:%s" % (m.group(1), m.group(2))]
    elif name.endswith(".csproj"):
        deps += re.findall(r'<PackageReference\s+Include="([^"]+)"', text)
    elif name == "Gemfile":
        deps += re.findall(r"""^\s*gem\s+['"]([^'"]+)['"]""", text, re.M)
    elif name == "composer.json":
        try:
            cj = json.loads(text)
        except ValueError:
            return []
        for k in ("require", "require-dev"):
            if isinstance(cj.get(k), dict):
                deps += list(cj[k])
    elif name == "Cargo.toml":
        sect = None
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("["):
                sect = s
            elif sect and "dependencies" in sect:
                m = re.match(r"([A-Za-z0-9_\-]+)\s*=", s)
                if m:
                    deps.append(m.group(1))
    return deps


MANIFESTS = {"package.json", "pyproject.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts",
             "Gemfile", "composer.json", "Cargo.toml"}


def is_manifest(name):
    return name in MANIFESTS or (name.startswith("requirements") and name.endswith(".txt")) or name.endswith(".csproj")


def scan(root, max_files=20000):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        raise InputError("%s is not a directory" % root)
    langs = Counter()
    found = defaultdict(lambda: defaultdict(set))   # role -> label -> {files}
    manifests, dockerfiles, base_images, compose, k8s_kinds = [], [], Counter(), [], Counter()
    k8s_files, helm, kustomize, tf_resources, tf_files, iac_other = [], [], [], Counter(), [], []
    ci, migrations, api, entry_points = [], [], [], []
    seen = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in (".github", ".circleci"))
        rel_dir = os.path.relpath(dirpath, root)
        rel_dir = "" if rel_dir == "." else rel_dir
        low_dir = rel_dir.replace(os.sep, "/").lower()
        if re.search(r"(^|/)(migrations?|db/migrate|alembic/versions|flyway|liquibase)$", low_dir):
            migrations.append(rel_dir.replace(os.sep, "/") + "/")
        for name in sorted(filenames):
            seen += 1
            if seen > max_files:
                raise InputError("more than %d files; pass a subfolder or --max-files" % max_files)
            rel = os.path.join(rel_dir, name).replace(os.sep, "/")
            path = os.path.join(dirpath, name)
            ext = os.path.splitext(name)[1].lower()
            if ext in EXT_LANG:
                langs[EXT_LANG[ext]] += 1
                if re.match(r"(main|index|app|server|program|application)\.", name.lower()) and rel.count("/") <= 3:
                    entry_points.append(rel)
            if is_manifest(name):
                text = read(path)
                if text is None:
                    continue
                manifests.append(rel)
                for dep in deps_from(name, rel, text):
                    for role, label in match_sig(dep):
                        found[role][label].add(rel)
            elif name == "Dockerfile" or name.endswith(".Dockerfile") or name.startswith("Dockerfile."):
                dockerfiles.append(rel)
                text = read(path) or ""
                for img in re.findall(r"^\s*FROM\s+(?:--\S+\s+)?([^\s]+)", text, re.M | re.I):
                    base_images[img.split("@")[0]] += 1
            elif name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
                compose.append(rel)
                text = read(path) or ""
                for img in re.findall(r"^\s+image:\s*['\"]?([^\s'\"]+)", text, re.M):
                    base_images[img] += 1
            elif name == "Chart.yaml":
                helm.append(rel)
            elif name in ("kustomization.yaml", "kustomization.yml"):
                kustomize.append(rel)
            elif ext == ".tf":
                tf_files.append(rel)
                text = read(path) or ""
                for t in re.findall(r'^\s*resource\s+"([a-z0-9_]+)"', text, re.M):
                    tf_resources[t] += 1
            elif ext == ".bicep" or name in ("Pulumi.yaml", "cdk.json", "serverless.yml", "serverless.yaml",
                                              "template.yaml", "samconfig.toml"):
                iac_other.append(rel)
            elif ext in (".yml", ".yaml"):
                if low_dir.startswith(".github/workflows"):
                    ci.append((rel, "GitHub Actions"))
                    continue
                text = read(path) or ""
                kinds = re.findall(r"^kind:\s*([A-Za-z]+)", text, re.M)
                if kinds and re.search(r"^apiVersion:", text, re.M):
                    k8s_files.append(rel)
                    for k in kinds:
                        k8s_kinds[k] += 1
                if re.search(r"^(openapi|swagger):", text, re.M):
                    api.append((rel, "OpenAPI"))
            elif ext == ".proto":
                api.append((rel, "gRPC / protobuf"))
            elif ext in (".graphql", ".gql"):
                api.append((rel, "GraphQL schema"))
            elif name == "schema.prisma":
                text = read(path) or ""
                models = re.findall(r"^model\s+(\w+)", text, re.M)
                found["orm"]["Prisma (%d models)" % len(models)].add(rel)
                for prov in re.findall(r'provider\s*=\s*"(postgresql|mysql|sqlite|mongodb|sqlserver|cockroachdb)"', text):
                    found["data store"][{"postgresql": "PostgreSQL", "mysql": "MySQL", "sqlite": "SQLite",
                                         "mongodb": "MongoDB", "sqlserver": "SQL Server",
                                         "cockroachdb": "CockroachDB"}[prov]].add(rel)
            elif ext == ".json" and re.search(r"(openapi|swagger)", name.lower()):
                api.append((rel, "OpenAPI"))
            if rel in CI_FILES:
                ci.append((rel, CI_FILES[rel]))
            if ext == ".sql" and re.match(r"(V\d+__|\d{3,})", name):
                d = rel_dir.replace(os.sep, "/") + "/"
                if d not in migrations:
                    migrations.append(d)
    return {
        "root": root,
        "files_scanned": seen,
        "languages": dict(langs.most_common()),
        "entry_points": entry_points[:10],
        "manifests": manifests,
        "stack": {role: {label: sorted(files) for label, files in sorted(found[role].items())}
                  for role in ROLE_ORDER if found.get(role)},
        "api_contracts": [{"file": f, "type": t} for f, t in api],
        "migrations": sorted(set(migrations)),
        "containers": {"dockerfiles": dockerfiles, "compose": compose,
                       "images": dict(base_images.most_common(10))},
        "kubernetes": {"manifests": len(k8s_files), "kinds": dict(k8s_kinds.most_common()),
                       "helm_charts": helm, "kustomize": kustomize, "files": k8s_files[:5]},
        "iac": {"terraform_files": len(tf_files), "terraform_resources": dict(tf_resources.most_common(25)),
                "other": iac_other},
        "ci_cd": [{"file": f, "tool": t} for f, t in ci],
    }


def _n(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def _files(fs, n=3):
    fs = list(fs)
    return ", ".join("`%s`" % f for f in fs[:n]) + (" (+%d)" % (len(fs) - n) if len(fs) > n else "")


def evidence_lines(r):
    """Suggested team.evidence entries for team_score.py (plain text, no quotes or colons)."""
    ev = {}
    c = r["containers"]
    if c["dockerfiles"]:
        ev["containers"] = "%s in the repo" % _n(len(c["dockerfiles"]), "Dockerfile")
    k = r["kubernetes"]
    if k["manifests"] or k["helm_charts"]:
        ev["kubernetes"] = "%s and %s in the repo" % (_n(k["manifests"], "Kubernetes manifest"),
                                                      _n(len(k["helm_charts"]), "Helm chart"))
    i = r["iac"]
    if i["terraform_files"] or i["other"]:
        parts = [_n(i["terraform_files"], "Terraform file")] if i["terraform_files"] else []
        if i["other"]:
            parts.append(_n(len(i["other"]), "other IaC file"))
        ev["iac"] = "%s in the repo" % " and ".join(parts)
    return ev


def to_markdown(r):
    L = ["**Codebase inventory** (%d files scanned, read-only)" % r["files_scanned"], ""]
    if r["languages"]:
        L.append("- **Languages:** " + ", ".join("%s (%d files)" % kv for kv in r["languages"].items()))
    if r["entry_points"]:
        L.append("- **Likely entry points:** " + _files(r["entry_points"], 5))
    for role in ROLE_ORDER:
        items = r["stack"].get(role)
        if items:
            L.append("- **%s:** %s" % (ROLE_TITLES[role], "; ".join(
                "%s (%s)" % (label, _files(fs, 2)) for label, fs in items.items())))
    if r["api_contracts"]:
        L.append("- **API contracts:** " + "; ".join("%s `%s`" % (a["type"], a["file"]) for a in r["api_contracts"][:5]))
    if r["migrations"]:
        L.append("- **Database migrations:** " + _files(r["migrations"]))
    c = r["containers"]
    if c["dockerfiles"] or c["compose"]:
        L.append("- **Containers:** %s (%s)%s%s" % (
            _n(len(c["dockerfiles"]), "Dockerfile"), _files(c["dockerfiles"]),
            "; compose %s" % _files(c["compose"]) if c["compose"] else "",
            "; images " + ", ".join(c["images"]) if c["images"] else ""))
    k = r["kubernetes"]
    if k["manifests"] or k["helm_charts"] or k["kustomize"]:
        L.append("- **Kubernetes:** %s (%s)%s" % (
            _n(k["manifests"], "manifest"), ", ".join("%s ×%d" % kv for kv in k["kinds"].items()),
            "; Helm %s" % _files(k["helm_charts"]) if k["helm_charts"] else ""))
    i = r["iac"]
    if i["terraform_files"] or i["other"]:
        res = ", ".join("%s ×%d" % kv for kv in list(i["terraform_resources"].items())[:12])
        L.append("- **IaC:** %s%s%s" % (
            _n(i["terraform_files"], "Terraform file"), " (%s)" % res if res else "",
            "; other: %s" % _files(i["other"]) if i["other"] else ""))
    if r["ci_cd"]:
        tools = sorted({x["tool"] for x in r["ci_cd"]})
        L.append("- **CI/CD:** %s (%s)" % (", ".join(tools), _files([x["file"] for x in r["ci_cd"]])))
    if len(L) == 2:
        L.append("- Nothing recognisable found: no manifests, IaC, containers or CI files.")
    ev = evidence_lines(r)
    if ev:
        L += ["", "Team-profile evidence: " + "; ".join("%s ← %s" % kv for kv in ev.items()) + "."]
    L += ["", "Detected from file names and declared dependencies only; read the code to confirm how each is used."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="inventory.py",
        description="Read-only inventory of an existing codebase: languages, frameworks, data stores, "
                    "messaging, cloud SDKs, API contracts, migrations, containers, Kubernetes, IaC and CI/CD, "
                    "with the files that show each.",
        epilog="Example: python3 inventory.py . --format markdown\nExit status: 0 ok, 2 invalid input.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", help="repository root to scan (default: .)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--max-files", type=int, default=20000)
    args = ap.parse_args(argv)
    try:
        r = scan(args.root, args.max_files)
    except InputError as exc:
        return fail(ap.prog, exc)
    if args.format == "json":
        r = dict(r, team_evidence=evidence_lines(r))
        json.dump(r, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(to_markdown(r) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
