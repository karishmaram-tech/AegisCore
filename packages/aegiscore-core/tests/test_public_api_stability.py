"""Stability snapshot — every public ``aegiscore-core`` name imports.

Locks in the public surface so accidental removal / rename fails CI.
Spec §6.1 enumerates the SemVer-stable surface plugin authors and
downstream consumers can rely on at v1.0; this test asserts each
listed name is importable from its declared module.

To intentionally remove or rename a public name:
  1. Update this manifest in the same commit
  2. Update the CHANGELOG (and migration guide if the rename breaks
     callers)
  3. Bump the major version if at 1.0+
"""

from __future__ import annotations

import importlib
from typing import Any

import pytest

# (module, name) pairs. Every entry must resolve to an importable
# attribute. Reorganize by category for readability.
CORE_PUBLIC_API: tuple[tuple[str, str], ...] = (
    # aegiscore_core.types.engagement
    ("aegiscore_core.types.engagement", "RoE"),
    ("aegiscore_core.types.engagement", "OPPLAN"),
    ("aegiscore_core.types.engagement", "Finding"),
    ("aegiscore_core.types.engagement", "Evidence"),
    ("aegiscore_core.types.engagement", "Objective"),
    ("aegiscore_core.types.engagement", "AttackPath"),
    ("aegiscore_core.types.engagement", "ObjectivePhase"),
    ("aegiscore_core.types.engagement", "ObjectiveStatus"),
    ("aegiscore_core.types.engagement", "OpsecLevel"),
    ("aegiscore_core.types.engagement", "C2Tier"),
    ("aegiscore_core.types.engagement", "FindingSeverity"),
    ("aegiscore_core.types.engagement", "FindingConfidence"),
    ("aegiscore_core.types.engagement", "RemediationPriority"),
    ("aegiscore_core.types.engagement", "EngagementType"),
    ("aegiscore_core.types.engagement", "ScopeEntry"),
    ("aegiscore_core.types.engagement", "EscalationContact"),
    # aegiscore_core.types.llm
    ("aegiscore_core.types.llm", "Tier"),
    ("aegiscore_core.types.llm", "AuthMethod"),
    ("aegiscore_core.types.llm", "ModelProfile"),
    ("aegiscore_core.types.llm", "Credentials"),
    ("aegiscore_core.types.llm", "ProxyConfig"),
    ("aegiscore_core.types.llm", "ModelAssignment"),
    ("aegiscore_core.types.llm", "LLMModelMapping"),
    # aegiscore_core.types.kg
    ("aegiscore_core.types.kg", "Node"),
    ("aegiscore_core.types.kg", "Edge"),
    ("aegiscore_core.types.kg", "NodeKind"),
    ("aegiscore_core.types.kg", "EdgeKind"),
    ("aegiscore_core.types.kg", "Severity"),
    ("aegiscore_core.types.kg", "KnowledgeGraph"),
    # aegiscore_core.types.roe — machine-readable RoE enforcement schema
    ("aegiscore_core.types.roe", "EnforcementMode"),
    ("aegiscore_core.types.roe", "ScopeRule"),
    ("aegiscore_core.types.roe", "MachineEnforcement"),
    ("aegiscore_core.types.roe", "Decision"),
    ("aegiscore_core.types.roe", "evaluate_target"),
    ("aegiscore_core.types.roe", "evaluate_command"),
    # aegiscore_core.protocols
    ("aegiscore_core.protocols", "BackendProtocol"),
    ("aegiscore_core.protocols", "MiddlewareProtocol"),
    ("aegiscore_core.protocols", "ToolProtocol"),
    ("aegiscore_core.protocols", "CallbackProtocol"),
    ("aegiscore_core.protocols", "LLMProtocol"),
    ("aegiscore_core.protocols", "SandboxProtocol"),
    ("aegiscore_core.protocols", "AgentProtocol"),
    # aegiscore_core.contracts.slots
    ("aegiscore_core.contracts.slots", "MiddlewareSlot"),
    ("aegiscore_core.contracts.slots", "SAFETY_CRITICAL_SLOTS"),
    ("aegiscore_core.contracts.slots", "SLOTS_PER_ROLE"),
    # aegiscore_core.contracts.contributions
    ("aegiscore_core.contracts.contributions", "ToolContribution"),
    ("aegiscore_core.contracts.contributions", "MiddlewareContribution"),
    ("aegiscore_core.contracts.contributions", "PromptContribution"),
    ("aegiscore_core.contracts.contributions", "SubAgentContribution"),
    ("aegiscore_core.contracts.contributions", "SafetyDeclaration"),
    # aegiscore_core.registry
    ("aegiscore_core.registry", "PluginRegistry"),
    ("aegiscore_core.registry", "PluginInfo"),
    ("aegiscore_core.registry", "PluginConflictWarning"),
    ("aegiscore_core.registry", "RoleRegistry"),
    ("aegiscore_core.registry", "RoleSpec"),
    ("aegiscore_core.registry", "RoleResolution"),
    ("aegiscore_core.registry", "MiddlewareInfo"),
    ("aegiscore_core.registry", "ToolInfo"),
    ("aegiscore_core.registry", "OverrideInfo"),
    ("aegiscore_core.registry", "SafetyRegistry"),
    ("aegiscore_core.registry", "SkillSourceRegistry"),
    # aegiscore_core.plugin_loader (still here for back-compat;
    # contracts will eventually split into contracts/, registry/ per
    # spec §9.1 but the public symbol set stays the same).
    ("aegiscore_core.plugin_loader", "PluginBundle"),
    ("aegiscore_core.plugin_loader", "SubAgentSpec"),
    ("aegiscore_core.plugin_loader", "is_bundle_enabled"),
    ("aegiscore_core.plugin_loader", "load_plugin_tools"),
    ("aegiscore_core.plugin_loader", "load_plugin_middleware"),
    ("aegiscore_core.plugin_loader", "load_plugin_callbacks"),
    ("aegiscore_core.plugin_loader", "load_plugin_skill_sources"),
    ("aegiscore_core.plugin_loader", "load_subagents_for_parent"),
    ("aegiscore_core.plugin_loader", "load_plugin_agents"),
    # aegiscore_core.utils
    ("aegiscore_core.utils.config", "DecepticonConfig"),
    ("aegiscore_core.utils.config", "LLMConfig"),
    ("aegiscore_core.utils.config", "load_config"),
    ("aegiscore_core.utils.logging", "configure_logging"),
    ("aegiscore_core.utils.logging", "get_logger"),
)


@pytest.mark.parametrize(("module_name", "attr"), CORE_PUBLIC_API)
def test_public_name_importable(module_name: str, attr: str) -> None:
    """Each (module, name) in the manifest must resolve.

    Failures indicate accidental removal or rename — fix the
    implementation, or update both this manifest and the CHANGELOG
    in the same commit.
    """
    module = importlib.import_module(module_name)
    value: Any = getattr(module, attr, None)
    assert value is not None, (
        f"{module_name}.{attr} returned None — accidental removal? "
        f"If intentional, update this manifest + CHANGELOG together."
    )


def test_manifest_count_unchanged() -> None:
    """Snapshot the manifest size so silent drift surfaces.

    Bumping the count is fine in either direction — the test
    documents the intentional change in the diff. Lowering without
    a major-version bump is an audit signal.
    """
    # Update this number deliberately when adding/removing public names.
    expected = 75
    actual = len(CORE_PUBLIC_API)
    assert actual == expected, (
        f"CORE_PUBLIC_API has {actual} entries, expected {expected}. "
        f"If intentional, bump this number AND update the CHANGELOG."
    )
