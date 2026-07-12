"""LangGraph Platform graph registry — OSS built-ins merged with plugins.

LangGraph Platform expects a graph manifest (``langgraph.json``) or the
``LANGSERVE_GRAPHS`` environment variable mapping each graph name to a
``module:attr`` path. Aegiscore's built-in agents are listed in the
``langgraph.json`` shipped with the repo. External packages add their own
agents by declaring entry-points in the ``aegiscore.agents`` group.

This module produces a merged manifest at runtime so external plugins
(e.g. a downstream plugin package shipped separately) can extend the available
graphs without editing ``langgraph.json``.

Typical usage in a container startup script:

    LANGSERVE_GRAPHS="$(python -m aegiscore.graph_registry)" \\
        langgraph dev --host 0.0.0.0 --port 2024
"""

from __future__ import annotations

import json

from aegiscore_core.plugin_loader import is_bundle_enabled, load_plugin_agents

# Built-in graphs split by bundle. ``build_langserve_graphs`` merges only
# the bundles active under DECEPTICON_PLUGINS / config file (see
# ``aegiscore_core.plugin_loader._enabled_bundles``). External plugin
# packages register agents under the ``aegiscore.agents`` entry-point
# group and are always loaded when installed.

# Standard bundle — official OSS main agent + subagents + soundwave.
STANDARD_GRAPHS: dict[str, str] = {
    "aegiscore": "./aegiscore/agents/standard/aegiscore.py:graph",
    "recon": "./aegiscore/agents/standard/recon.py:graph",
    "soundwave": "./aegiscore/agents/standard/soundwave.py:graph",
    "exploit": "./aegiscore/agents/standard/exploit.py:graph",
    "postexploit": "./aegiscore/agents/standard/postexploit.py:graph",
    "analyst": "./aegiscore/agents/standard/analyst.py:graph",
    "reverser": "./aegiscore/agents/standard/reverser.py:graph",
    "contract_auditor": "./aegiscore/agents/standard/contract_auditor.py:graph",
    "cloud_hunter": "./aegiscore/agents/standard/cloud_hunter.py:graph",
    "ad_operator": "./aegiscore/agents/standard/ad_operator.py:graph",
    "blue_cell": "./aegiscore/agents/standard/blue_cell.py:graph",
    "phisher": "./aegiscore/agents/standard/phisher.py:graph",
    "mobile_operator": "./aegiscore/agents/standard/mobile_operator.py:graph",
    "wireless_operator": "./aegiscore/agents/standard/wireless_operator.py:graph",
    "osint_operator": "./aegiscore/agents/standard/osint_operator.py:graph",
    "iot_operator": "./aegiscore/agents/standard/iot_operator.py:graph",
    "ics_operator": "./aegiscore/agents/standard/ics_operator.py:graph",
    "forensicator": "./aegiscore/agents/standard/forensicator.py:graph",
    "supply_chain_operator": "./aegiscore/agents/standard/supply_chain_operator.py:graph",
}

# Plugins bundle — vulnresearch family (community-plugin shape demonstrated
# from inside OSS). Opt-in via ``DECEPTICON_PLUGINS=standard,plugins`` or
# ``[plugins] enabled = ["standard", "plugins"]`` in ``.aegiscore.toml``.
PLUGIN_GRAPHS: dict[str, str] = {
    "vulnresearch": "./aegiscore/agents/plugins/vulnresearch.py:graph",
    "scanner": "./aegiscore/agents/plugins/scanner.py:graph",
    "detector": "./aegiscore/agents/plugins/detector.py:graph",
    "verifier": "./aegiscore/agents/plugins/verifier.py:graph",
    "patcher": "./aegiscore/agents/plugins/patcher.py:graph",
    "exploiter": "./aegiscore/agents/plugins/exploiter.py:graph",
}

# Mapping from bundle name to its graph dict — used by build_langserve_graphs.
_BUNDLE_TO_GRAPHS: dict[str, dict[str, str]] = {
    "standard": STANDARD_GRAPHS,
    "plugins": PLUGIN_GRAPHS,
}

# Backward-compat alias — full unfiltered manifest (every OSS-shipped graph).
# Prefer ``build_langserve_graphs()`` which respects DECEPTICON_PLUGINS.
BUILTIN_GRAPHS: dict[str, str] = {**STANDARD_GRAPHS, **PLUGIN_GRAPHS}


def build_langserve_graphs() -> dict[str, str]:
    """Return ``{name: module:graph}`` for active bundles + discovered plugins.

    OSS-internal bundles (``standard``, ``plugins``) are filtered by
    ``DECEPTICON_PLUGINS`` / config-file allowlist. Plugin-contributed
    agents (registered under the ``aegiscore.agents`` entry-point group
    by external packages) are always merged in — installing the package
    is the user's opt-in.

    Name collisions: plugin-contributed agents override built-in entries.
    """
    merged: dict[str, str] = {}
    for bundle_name, graphs in _BUNDLE_TO_GRAPHS.items():
        if is_bundle_enabled(bundle_name):
            merged.update(graphs)
    merged.update(load_plugin_agents())
    return merged


def emit_langserve_env() -> str:
    """Serialize the merged manifest as compact JSON for ``LANGSERVE_GRAPHS``."""
    return json.dumps(build_langserve_graphs(), separators=(",", ":"))


def main() -> None:
    """CLI entry: print the merged graph manifest as JSON to stdout."""
    print(emit_langserve_env())


if __name__ == "__main__":
    main()
