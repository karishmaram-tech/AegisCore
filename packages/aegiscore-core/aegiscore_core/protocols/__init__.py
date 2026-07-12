"""Plugin-author Protocols for the Aegiscore contract layer.

Each Protocol declares the duck-type interface plugin authors must
implement to contribute a tool, middleware, callback, etc. Decorated
with ``@runtime_checkable`` so ``isinstance(obj, MiddlewareProtocol)``
works at runtime; static type checkers verify shape at plugin compile
time.

Submodules:

  * ``backend``    — deepagents-style filesystem backend
  * ``middleware`` — langchain agent middleware
  * ``tool``       — langchain ``@tool``-style callable
  * ``callback``   — langchain ``BaseCallbackHandler``
  * ``llm``        — bound language model
  * ``sandbox``    — sandbox transport (HTTPSandbox or equivalent)
  * ``agent``      — compiled agent / sub-agent

All Protocols ship in this contract layer so plugin authors can
declare conformance without depending on the framework runtime.
"""

from __future__ import annotations

from aegiscore_core.protocols.agent import AgentProtocol
from aegiscore_core.protocols.backend import BackendProtocol
from aegiscore_core.protocols.callback import CallbackProtocol
from aegiscore_core.protocols.llm import LLMProtocol
from aegiscore_core.protocols.middleware import MiddlewareProtocol
from aegiscore_core.protocols.sandbox import SandboxProtocol
from aegiscore_core.protocols.tool import ToolProtocol

__all__ = [
    "AgentProtocol",
    "BackendProtocol",
    "CallbackProtocol",
    "LLMProtocol",
    "MiddlewareProtocol",
    "SandboxProtocol",
    "ToolProtocol",
]
