"""Utility modules for the Aegiscore contract layer.

Pure stdlib + pydantic helpers — config loaders, logging setup. Imported
by the framework (``aegiscore_core.utils.config``, ``aegiscore_core.utils.logging``
shims) and freely usable by plugin authors.
"""

from __future__ import annotations

from aegiscore_core.utils import config, logging

__all__ = ["config", "logging"]
