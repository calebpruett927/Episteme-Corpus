# src/umcp/kernel.py
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional

import numpy as np

from umcp.closures import DriftClosure, GammaOmegaPower
from umcp.contract import FrozenContract


@dataclass(frozen=True, slots=True)
class Tier1Row:
    """
    Tier-1 kernel row for a single time index.

    Symbols (Tier-1 reserved):
      ω  : drift
      F  : fidelity (= 1 - ω, clipped to [0,1] by convention)
      S  : normalized binary entropy mean across coordinates
      C  : curvature (2nd difference magnitude)
      τ_R: return lag (finite if a prior state re-enters within tol_id)
      IC : integrity composite in (0,1]
      κ  : ln(IC)
    """
    t: int
    omega: float
    F: float
    S: float
    C: float
    tau_R: float
    IC: float
    kappa: float


def _lp_mean_norm(v: np.ndarray, p: float, eps: float) -> float:
    # Mean Lp norm per coordinate, stabilized.
    vp = np.abs(v) + eps
    return float(np.mean(vp ** p) ** (1.0 / p))


def _binary_entropy_mean(x: np.ndarray, eps: float) -> float:
    # x assumed in [0,1]. Normalized by ln(2) so range ~[0,1].
    x1 = np.clip(x, eps, 1.0 - eps)
    h = -(x1 * np.log(x1) + (1.0 - x1) * np.log(1.0 - x1))
    return float(np.mean(h) / math.log(2.0))


def _curvature(x_t: np.ndarray, x_t1: np.ndarray, x_t2: np.ndarray, p: float, eps: float) -> float:
    # Discrete second difference magnitude per coordinate.
    dd = x_t - 2.0 * x_t1 + x_t2
    return _lp_mean_norm(dd, p=p, eps=eps)


def _return_lag(psi: np.ndarray, t: int, tol_id: float, lookback: int, p: float, eps: float) -> float:
    """
    τ_R(t): smallest L in [1, min(lookback,t)] s.t. ||ψ[t] - ψ[t-L]||_p_mean <= tol_id.
    If none found, return +inf (∞_rec policy).
    """
    if t <= 0:
        return float("inf")
    max_lag = min(lookback, t)
    x_t = psi[t]
    for L in range(1, max_lag + 1):
        d = _lp_mean_norm(x_t - psi[t - L], p=p, eps=eps)
        if d <= tol_id:
            return float(L)
    return float("inf")


def compute_tier1_series(
    psi: np.ndarray,
    contract: FrozenContract,
    drift_closure: Optional[DriftClosure] = None,
) -> List[Tier1Row]:
    """
    Compute Tier-1 series on an admitted trace Ψ(t) ∈ [a,b]^n.

    Deterministic, audit-friendly definitions:
      ω(t)    = mean-Lp norm of Δψ(t) = ψ(t) - ψ(t-1)
      F(t)    = clip(1 - ω(t), 0, 1)
      S(t)    = mean normalized binary entropy across coordinates
      C(t)    = mean-Lp norm of second difference
      τ_R(t)  = smallest lag returning within tol_id (else +inf)
      IC(t)   = exp(-(Γ(ω) + α*C + λ*S))
      κ(t)    = ln(IC(t))  (identity enforced)
    """
    x = np.asarray(psi, dtype=float)
    if x.ndim != 2:
        raise ValueError(f"psi must be 2D array shaped (T,n); got shape={x.shape}")

    eps = float(contract.epsilon)
    p = float(contract.p)
    alpha = float(contract.alpha)
    lam = float(contract.lam)

    Gamma = drift_closure if drift_closure is not None else GammaOmegaPower(p=p, epsilon=eps)

    T = x.shape[0]
    rows: List[Tier1Row] = []

    for t in range(T):
        if t == 0:
            omega = 0.0
            C = 0.0
        else:
            omega = _lp_mean_norm(x[t] - x[t - 1], p=p, eps=eps)
            if t >= 2:
                C = _curvature(x[t], x[t - 1], x[t - 2], p=p, eps=eps)
            else:
                C = 0.0

        F = 1.0 - omega
        if F < 0.0:
            F = 0.0
        elif F > 1.0:
            F = 1.0

        S = _binary_entropy_mean(x[t], eps=eps)
        tau_R = _return_lag(x, t=t, tol_id=float(contract.tol_id), lookback=int(contract.tau_lookback), p=p, eps=eps)

        D_omega = float(Gamma(omega))
        D_C = alpha * C
        D_S = lam * S

        # IC in (0,1], κ = ln(IC) identity by construction.
        kappa = -(D_omega + D_C + D_S)
        IC = math.exp(kappa)

        rows.append(
            Tier1Row(
                t=t,
                omega=float(omega),
                F=float(F),
                S=float(S),
                C=float(C),
                tau_R=float(tau_R),
                IC=float(IC),
                kappa=float(kappa),
            )
        )

    return rows
