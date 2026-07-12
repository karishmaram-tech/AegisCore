"""Aegiscore middleware - custom AgentMiddleware implementations."""

from aegiscore.middleware.budget import BudgetEnforcementMiddleware
from aegiscore.middleware.engagement import EngagementContextMiddleware
from aegiscore.middleware.event_logging import EventLogMiddleware
from aegiscore.middleware.filesystem import FilesystemMiddleware
from aegiscore.middleware.hitl import (
    DEFAULT_HIGH_IMPACT_POLICY,
    ApprovalDecision,
    ApprovalPolicyRule,
    ApprovalRequest,
    ApprovalTransport,
    FileBackedApprovalTransport,
    HITLApprovalMiddleware,
    InProcessApprovalTransport,
)
from aegiscore.middleware.kg import KGMiddleware
from aegiscore.middleware.notifications import (
    SandboxNotificationMiddleware,
)
from aegiscore.middleware.opplan import OPPLANMiddleware
from aegiscore.middleware.prompt_injection_shield import (
    PromptInjectionShieldMiddleware,
)
from aegiscore.middleware.roe import (
    RoEEnforcementMiddleware,  # compat alias, removed at 2.0.0
    RoEGuardrailMiddleware,
)
from aegiscore.middleware.skillogy import SkillogyMiddleware, maybe_install_skillogy
from aegiscore.middleware.skills import SkillsMiddleware
from aegiscore.middleware.untrusted_output import UntrustedOutputMiddleware

__all__ = [
    "ApprovalDecision",
    "ApprovalPolicyRule",
    "ApprovalRequest",
    "ApprovalTransport",
    "BudgetEnforcementMiddleware",
    "DEFAULT_HIGH_IMPACT_POLICY",
    "EngagementContextMiddleware",
    "EventLogMiddleware",
    "FileBackedApprovalTransport",
    "FilesystemMiddleware",
    "HITLApprovalMiddleware",
    "InProcessApprovalTransport",
    "KGMiddleware",
    "OPPLANMiddleware",
    "PromptInjectionShieldMiddleware",
    "RoEEnforcementMiddleware",
    "RoEGuardrailMiddleware",
    "SandboxNotificationMiddleware",
    "SkillogyMiddleware",
    "SkillsMiddleware",
    "UntrustedOutputMiddleware",
    "maybe_install_skillogy",
]
