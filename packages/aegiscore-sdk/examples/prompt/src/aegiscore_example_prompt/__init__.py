"""Prompt fragments contributed to one or more roles."""

from __future__ import annotations

from aegiscore_sdk import PromptContribution


def get_contribution() -> PromptContribution:
    """Plugin factory called by the framework's prompt loader."""
    return PromptContribution(
        fragments={"recon": "<aegiscore_example_prompt>...</aegiscore_example_prompt>"},
        mode="append",
        roles=("recon",),
    )
