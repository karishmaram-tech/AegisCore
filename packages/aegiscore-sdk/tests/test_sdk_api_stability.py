"""Stability snapshot — every public ``aegiscore-sdk`` name imports.

Spec §6.3 lists the SDK single-import surface that plugin authors
rely on. This test locks in the 23 stable symbols + the testing
fakes so a removed re-export fails CI.

See ``packages/aegiscore-core/tests/test_public_api_stability.py``
for the corresponding core-layer snapshot.
"""

from __future__ import annotations

import importlib
from typing import Any

import pytest

SDK_PUBLIC_API: tuple[tuple[str, str], ...] = (
    # Protocols (7)
    ("aegiscore_sdk", "BackendProtocol"),
    ("aegiscore_sdk", "MiddlewareProtocol"),
    ("aegiscore_sdk", "ToolProtocol"),
    ("aegiscore_sdk", "CallbackProtocol"),
    ("aegiscore_sdk", "LLMProtocol"),
    ("aegiscore_sdk", "SandboxProtocol"),
    ("aegiscore_sdk", "AgentProtocol"),
    # Slot enum + constants (3)
    ("aegiscore_sdk", "MiddlewareSlot"),
    ("aegiscore_sdk", "SAFETY_CRITICAL_SLOTS"),
    ("aegiscore_sdk", "SLOTS_PER_ROLE"),
    # Focused contributions (5)
    ("aegiscore_sdk", "ToolContribution"),
    ("aegiscore_sdk", "MiddlewareContribution"),
    ("aegiscore_sdk", "PromptContribution"),
    ("aegiscore_sdk", "SubAgentContribution"),
    ("aegiscore_sdk", "SafetyDeclaration"),
    # Plugin loader (3)
    ("aegiscore_sdk", "PluginBundle"),
    ("aegiscore_sdk", "SubAgentSpec"),
    ("aegiscore_sdk", "is_bundle_enabled"),
    # Registry (8)
    ("aegiscore_sdk", "PluginRegistry"),
    ("aegiscore_sdk", "PluginInfo"),
    ("aegiscore_sdk", "PluginConflictWarning"),
    ("aegiscore_sdk", "RoleRegistry"),
    ("aegiscore_sdk", "RoleSpec"),
    ("aegiscore_sdk", "RoleResolution"),
    ("aegiscore_sdk", "SafetyRegistry"),
    ("aegiscore_sdk", "SkillSourceRegistry"),
    # Testing fakes (3)
    ("aegiscore_sdk.testing", "FakeBackend"),
    ("aegiscore_sdk.testing", "FakeLLM"),
    ("aegiscore_sdk.testing", "FakeSandbox"),
    # Scaffold entry (CLI also wired via [project.scripts])
    ("aegiscore_sdk.scaffold", "app"),
)


@pytest.mark.parametrize(("module_name", "attr"), SDK_PUBLIC_API)
def test_sdk_public_name_importable(module_name: str, attr: str) -> None:
    module = importlib.import_module(module_name)
    value: Any = getattr(module, attr, None)
    assert value is not None, (
        f"{module_name}.{attr} returned None — accidental removal? "
        f"If intentional, update this manifest + CHANGELOG together."
    )


def test_sdk_manifest_count_unchanged() -> None:
    """Snapshot the manifest size."""
    expected = 30
    actual = len(SDK_PUBLIC_API)
    assert actual == expected, (
        f"SDK_PUBLIC_API has {actual} entries, expected {expected}. "
        f"If intentional, bump this number AND update the CHANGELOG."
    )
