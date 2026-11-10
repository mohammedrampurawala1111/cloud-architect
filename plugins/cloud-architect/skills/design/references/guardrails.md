# Org guardrails (read only when there is an org profile or stated platform rules)

Applies when the repo has `.cloud-architect/org.yaml` **or** the user states
platform rules in the conversation (approved clouds, regions or services,
forbidden components). The check runs inside the single `plan.py` call:

- With the file: add `--org .cloud-architect/org.yaml` to the `plan.py` command.
- Rules from the conversation: add an `org:` block to the same stdin document,
  with `clouds`, `regions`, `approved_services`, `forbidden_classes` as block
  lists (one `- item` per line), for example:

```yaml
org:
  name: Acme
  clouds:
    - aws
  regions:
    - eu-central-1
  approved_services:
    - ECS on Fargate
    - RDS for PostgreSQL
  forbidden_classes:
    - self_hosted_database
```

Give `provider` and `region` per option (override per component), and
`global: true` for edge services with no region (CDN, DNS).

Paste the script's guardrails tables verbatim. For each exception either change
the design to fit, or keep it and write an **exception ADR** ("Exception: use
<product> outside the approved list"), with:
- why the approved alternative doesn't meet the requirement;
- what supporting it adds (another service to run, skills, upgrades);
- `Deciders:` the org owner named in the profile, or the decision-maker.

Count exceptions in the options comparison and the decision brief: an option
needing several exceptions is a real cost even if it is cheaper. Use the org
profile's clouds, regions, approved services and platform (IaC, CI/CD,
observability) first when mapping.
