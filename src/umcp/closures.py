# src/umcp/closures.py
from __future__ import annotations

from dataclasses import dataclass
import math


class DriftClosure:
    """Protocol-like base for Γ(ω) closures used to compute drift-cost D_ω."""
    def __call__(self, omega: float) -> float:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class GammaOmegaPower(DriftClosure):
    """
    Γ(ω; p, ε) = max(ω, 0)^p + ε

    - Monotone in ω for ω>=0
    - Smooth enough for finite-difference sensitivity
    """
    p: float = 3.0
    epsilon: float = 1e-8

    def __call__(self, omega: float) -> float:
        w = omega if omega > 0.0 else 0.0
        return (w ** self.p) + self.epsilon


@dataclass(frozen=True, slots=True)
class GammaNegLogOneMinusOmega(DriftClosure):
    """
    Γ(ω; ε) = -ln(max(1-ω, ε))

    Useful when ω is interpreted as a “failure probability”-like drift.
    """
    epsilon: float = 1e-8

    def __call__(self, omega: float) -> float:
        x = 1.0 - omega
        if x < self.epsilon:
            x = self.epsilon
        return -math.log(x)
