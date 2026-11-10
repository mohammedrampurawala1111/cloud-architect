# Org guardrails (read only when there is an org profile or stated platform rules)

Applies when the repo has `.cloud-architect/org.yaml` **or** the user states
platform rules in the conversation (approved clouds, regions or services,
forbidden components).

Rules come from `.cloud-architect/org.yaml` or the conversation: allowed
`clouds`, `regions`, `approved_services` (product names), `approved_classes`,
`forbidden_classes`. Compare names ignoring case, `-` and `_`. For each
component of each option (provider and region per option unless the component
says otherwise):

1. **Cloud:** with an allowed list, the provider must be on it; no provider
   given counts as an exception.
2. **Region:** with an allowed list, the region must be on it, except edge
   services with no region (CDN, DNS); no region given counts as an exception.
3. **Forbidden class:** a component of a forbidden class is an exception.
4. **Approved:** with an approved list, the product or the class must be on it
   (a forbidden component is reported once, under rule 3).

A component with any failing rule needs one exception. Output:

```markdown
**Org guardrails: Acme**

| Option | Exceptions | Verdict |
|---|---|---|
| A. Managed containers | 0 | fits guardrails |
| B. Kubernetes | 2 | needs 2 exception ADRs |

| Option | Component | Product | Rule | Why it needs an exception |
|---|---|---|---|---|
| B. Kubernetes | Cluster | EKS | approved services | EKS is not on the approved list |
| B. Kubernetes | Queue | SQS | region | us-east-1 is not an approved region |
```

Each exception needs an exception ADR signed off by the org owner, or a change
to the design (see `design` → `references/guardrails.md`).

Give `provider` and `region` per option (override per component), and
`global: true` for edge services with no region (CDN, DNS).

For each exception either change
the design to fit, or keep it and write an **exception ADR** ("Exception: use
<product> outside the approved list"), with:
- why the approved alternative doesn't meet the requirement;
- what supporting it adds (another service to run, skills, upgrades);
- `Deciders:` the org owner named in the profile, or the decision-maker.

Count exceptions in the options comparison and the decision brief: an option
needing several exceptions is a real cost even if it is cheaper. Use the org
profile's clouds, regions, approved services and platform (IaC, CI/CD,
observability) first when mapping.
