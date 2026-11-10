"""Shared helpers for the cloud-architect scripts (standard library only)."""

import difflib
import json
import sys

from _miniyaml import YamlError, loads as yaml_loads


class InputError(ValueError):
    """Bad or unsupported input; scripts exit with status 2."""


# Component classes and complexity weights. Mirrors the weight table in
# skills/team-fit/SKILL.md (examples in skills/team-fit/references/component-classes.md).
COMPONENT_CLASSES = {
    # weight 1
    "serverless_functions": 1,
    "paas": 1,
    "managed_database": 1,
    "object_storage": 1,
    "managed_queue": 1,
    "managed_auth": 1,
    "cdn": 1,
    "static_site": 1,
    "managed_secrets": 1,
    "managed_scheduler": 1,
    "managed_dns": 1,
    "managed_registry": 1,
    "managed_observability": 1,
    "managed_ci_cd": 1,
    "managed_llm_api": 1,
    # weight 2
    "managed_containers": 2,
    "managed_cache": 2,
    "api_gateway_custom_auth": 2,
    "managed_search": 2,
    "event_bus": 2,
    "managed_workflow": 2,
    "managed_warehouse": 2,
    "managed_stream": 2,
    "managed_ml_endpoint": 2,
    "vm": 2,
    "waf": 2,
    "private_networking": 2,
    # weight 3
    "managed_kubernetes": 3,
    "self_run_broker": 3,
    "stream_processing": 3,
    "multiple_db_engines": 3,
    "vpn_hybrid_networking": 3,
    "gpu_serving_self_managed": 3,
    "gitops": 3,
    # weight 4
    "service_mesh": 4,
    "self_hosted_database": 4,
    "multi_region_active_active": 4,
    "custom_autoscaling": 4,
    "own_observability_stack": 4,
    # weight 5
    "multi_cloud_active_active": 5,
    "self_run_kubernetes_control_plane": 5,
    "on_prem_cloud_federation": 5,
}


def read_text(path):
    try:
        if path == "-":
            return sys.stdin.read()
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc.strerror or exc))


def load_data(path):
    """Load JSON or the supported YAML subset from a path ('-' = stdin)."""
    text = read_text(path)
    stripped = text.lstrip()
    if not stripped:
        raise InputError("%s is empty" % ("stdin" if path == "-" else path))
    if stripped[0] in "{[":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            # Could still be a YAML flow document; fall through.
            json_error = exc
        else:
            json_error = None
    else:
        json_error = None
    try:
        return yaml_loads(text)
    except YamlError as exc:
        if json_error is not None:
            raise InputError("invalid JSON (%s)" % json_error)
        raise InputError("invalid YAML: %s" % exc)


def component_weight(comp, where):
    """Return the complexity weight for a component dict.

    Accepts an explicit integer ``weight`` (1-5) or a ``class`` from
    COMPONENT_CLASSES. An explicit weight wins.
    """
    if not isinstance(comp, dict):
        raise InputError("%s: each component must be an object, got %r" % (where, comp))
    if comp.get("weight") is not None:
        w = comp["weight"]
        if isinstance(w, bool) or not isinstance(w, (int, float)) or int(w) != w or not 1 <= w <= 5:
            raise InputError("%s: weight must be an integer 1-5, got %r" % (where, w))
        return int(w)
    cls = comp.get("class")
    if cls is None:
        raise InputError("%s: give either 'class' or 'weight'" % where)
    if cls not in COMPONENT_CLASSES:
        hint = difflib.get_close_matches(str(cls), COMPONENT_CLASSES.keys(), n=3)
        raise InputError(
            "%s: unknown class %r%s (see --list-classes)"
            % (where, cls, "; did you mean " + ", ".join(hint) + "?" if hint else "")
        )
    return COMPONENT_CLASSES[cls]


def classes_by_weight():
    out = {}
    for name, w in sorted(COMPONENT_CLASSES.items()):
        out.setdefault(w, []).append(name)
    return out


def fail(prog, exc):
    sys.stderr.write("%s: error: %s\n" % (prog, exc))
    return 2
