# src/umcp/tier0/__init__.py
"""
Tier-0: trace admission.

Tier-0 produces admitted Ψ(t) ∈ [0,1]^n with explicit OOR handling and flags.
"""

from .admit import AdmittedTrace, admit_trace

__all__ = ["AdmittedTrace", "admit_trace"]
