# src/umcp/contract.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


FacePolicy = Literal["pre_clip"]
OORPolicy = Literal["clip_and_flag"]
TauPolicy = Literal["inf_rec"]


@dataclass(frozen=True, slots=True)
class FrozenContract:
    """
    Canonical reproducibility boundary.

    Defaults align to UMA.INTSTACK.v1-like values described in your pipeline:
      (a,b)=(0,1), face=pre_clip, ε=1e-8, p=3, α=1, λ=0.2, η=1e-3,
      tol_seam=0.005, tol_id=1e-9, OOR=clip_and_flag, τ_R=∞_rec.
    """

    # Bounds
    a: float = 0.0
    b: float = 1.0
    face: FacePolicy = "pre_clip"
    oor: OORPolicy = "clip_and_flag"

    # Numerics / norms
    epsilon: float = 1e-8
    p: float = 3.0

    # Integrity weights (canonical symbols)
    alpha: float = 1.0  # curvature weight (D_C = alpha * C)
    lam: float = 0.2  # entropy weight (D_S = lam * S)
    eta: float = 1e-3  # generic step size placeholder

    # Return policy
    tau_policy: TauPolicy = "inf_rec"
    tau_lookback: int = 256  # max lag to search when computing τ_R

    # Weld tolerances
    tol_seam: float = 0.005
    tol_id: float = 1e-9

    # Regime gates (defaults)
    stable_omega_max: float = 0.038
    stable_F_min: float = 0.90
    stable_S_max: float = 0.15
    stable_C_max: float = 0.14

    watch_omega_max: float = 0.30  # collapse if ω >= watch_omega_max

    # Metadata
    tz: str = "America/Chicago"

    def clamp(self, x: float) -> float:
        if x < self.a:
            return self.a
        if x > self.b:
            return self.b
        return x
