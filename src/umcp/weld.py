# src/umcp/weld.py
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional

from umcp.closures import DriftClosure, GammaOmegaPower
from umcp.contract import FrozenContract
from umcp.kernel import Tier1Row


@dataclass(frozen=True, slots=True)
class SS1mWeld:
    """
    Compact weld receipt (SS1m-like).

    Core fields:
      Δκ_ledger = κ1 - κ0 = ln(IC1/IC0)
      ir        = IC1/IC0
      Δκ_budget = R·τ_R − (D_ω + D_C)
      s         = Δκ_budget − Δκ_ledger
      PASS      = τ_R finite AND |s|≤tol_seam AND |ir-exp(Δκ_ledger)|≤tol_id
    """
    kappa0: float
    kappa1: float
    IC0: float
    IC1: float
    delta_kappa_ledger: float
    ir: float
    delta_kappa_budget: float
    seam_residual: float
    tau_R: float
    R: float
    passed: bool


def evaluate_weld(
    pre: Tier1Row,
    post: Tier1Row,
    contract: FrozenContract,
    drift_closure: Optional[DriftClosure] = None,
) -> SS1mWeld:
    """
    Evaluate a PRE→POST weld at a comparison point.

    Uses the weld law you specified:
      Δκ_ledger = ln(IC1/IC0)
      ir        = IC1/IC0
      Δκ_budget = R·τ_R − (D_ω + D_C), with D_ω=Γ(ω), D_C=α·C
      s         = budget − ledger
      PASS iff τ_R finite AND |s|≤tol_seam AND |ir−exp(Δκ_ledger)|≤tol_id

    Note:
      - R is set to 1 if τ_R is finite, else 0 (typed censoring idea).
      - τ_R is taken from the POST row (the “new” regime being welded into).
    """
    eps = float(contract.epsilon)
    p = float(contract.p)
    alpha = float(contract.alpha)

    Gamma = drift_closure if drift_closure is not None else GammaOmegaPower(p=p, epsilon=eps)

    IC0 = float(pre.IC)
    IC1 = float(post.IC)

    # Ledger side
    delta_kappa_ledger = math.log(IC1 / IC0) if (IC0 > 0.0 and IC1 > 0.0) else float("nan")
    ir = IC1 / IC0 if IC0 > 0.0 else float("inf")

    # Budget side
    tau_R = float(post.tau_R)
    finite_tau = math.isfinite(tau_R)
    R = 1.0 if finite_tau else 0.0

    D_omega = float(Gamma(float(post.omega)))
    D_C = alpha * float(post.C)

    delta_kappa_budget = (R * tau_R) - (D_omega + D_C)
    seam_residual = delta_kappa_budget - delta_kappa_ledger

    # Identity check ir == exp(Δκ_ledger)
    id_err = abs(ir - math.exp(delta_kappa_ledger)) if math.isfinite(delta_kappa_ledger) else float("inf")

    passed = (
        finite_tau
        and math.isfinite(seam_residual)
        and abs(seam_residual) <= float(contract.tol_seam)
        and id_err <= float(contract.tol_id)
    )

    return SS1mWeld(
        kappa0=float(pre.kappa),
        kappa1=float(post.kappa),
        IC0=IC0,
        IC1=IC1,
        delta_kappa_ledger=float(delta_kappa_ledger),
        ir=float(ir),
        delta_kappa_budget=float(delta_kappa_budget),
        seam_residual=float(seam_residual),
        tau_R=float(tau_R),
        R=float(R),
        passed=bool(passed),
    )
