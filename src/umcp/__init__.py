# src/umcp/__init__.py
"""
UMCP platform reference package.

This package implements:
- Tier-0 trace admission (bounded Ψ(t) ∈ [0,1]^n under a frozen contract)
- Tier-1 kernel series (ω, F, S, C, τ_R, IC, κ)
- Closures (Γ) for drift cost D_ω
- Weld evaluation (SS1m-style compact receipt)
- Regime classification (Stable / Watch / Collapse)

Tier-1 symbol names are reserved to: {ω, F, S, C, τ_R, IC, κ}.
"""

from .contract import FrozenContract
from .closures import GammaOmegaPower, GammaNegLogOneMinusOmega
from .eid import prime_pi, EIDCounts, eid_checksum, delta_kappa_eid
from .kernel import Tier1Row, compute_tier1_series
from .weld import SS1mWeld, evaluate_weld

__all__ = [
    "FrozenContract",
    "GammaOmegaPower",
    "GammaNegLogOneMinusOmega",
    "prime_pi",
    "EIDCounts",
    "eid_checksum",
    "delta_kappa_eid",
    "Tier1Row",
    "compute_tier1_series",
    "SS1mWeld",
    "evaluate_weld",
]
