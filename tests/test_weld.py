import math

from umcp.contract import FrozenContract
from umcp.kernel import Tier1Row
from umcp.weld import evaluate_weld


def test_weld_passes_when_budget_closes_ledger():
    contract = FrozenContract()
    eps = contract.epsilon

    # Construct PRE row
    pre = Tier1Row(
        t=0,
        omega=0.0,
        F=1.0,
        S=0.0,
        C=0.0,
        tau_R=float("inf"),
        IC=1.0,
        kappa=0.0,
    )

    # Choose POST so that:
    # Δκ_budget = R·τ_R − (D_ω + D_C)
    # Here omega=0 => D_ω = eps (GammaOmegaPower), C=0 => D_C=0, τ_R=2 => R=1
    # So Δκ_budget = 2 - eps
    tau_R = 2.0
    delta_kappa_budget_target = tau_R - eps

    IC1 = math.exp(delta_kappa_budget_target) * pre.IC
    kappa1 = math.log(IC1)

    post = Tier1Row(
        t=1,
        omega=0.0,
        F=1.0,
        S=0.0,
        C=0.0,
        tau_R=tau_R,
        IC=IC1,
        kappa=kappa1,
    )

    weld = evaluate_weld(pre=pre, post=post, contract=contract)

    assert weld.passed is True
    assert math.isclose(weld.delta_kappa_budget, weld.delta_kappa_ledger, rel_tol=0.0, abs_tol=1e-10)
    assert abs(weld.seam_residual) <= contract.tol_seam
    assert math.isfinite(weld.tau_R)


def test_weld_fails_if_tauR_is_infinite():
    contract = FrozenContract()

    pre = Tier1Row(t=0, omega=0.0, F=1.0, S=0.0, C=0.0, tau_R=float("inf"), IC=1.0, kappa=0.0)
    post = Tier1Row(t=1, omega=0.0, F=1.0, S=0.0, C=0.0, tau_R=float("inf"), IC=1.0, kappa=0.0)

    weld = evaluate_weld(pre=pre, post=post, contract=contract)
    assert weld.passed is False


def test_weld_fails_if_seam_residual_exceeds_tolerance():
    contract = FrozenContract()

    pre = Tier1Row(t=0, omega=0.0, F=1.0, S=0.0, C=0.0, tau_R=float("inf"), IC=1.0, kappa=0.0)

    # Make tau_R finite but force ledger far from budget by setting IC1 arbitrarily
    post = Tier1Row(
        t=1,
        omega=0.0,
        F=1.0,
        S=0.0,
        C=0.0,
        tau_R=1.0,
        IC=0.01,              # arbitrary
        kappa=math.log(0.01),
    )

    weld = evaluate_weld(pre=pre, post=post, contract=contract)
    assert weld.passed is False
    assert abs(weld.seam_residual) > contract.tol_seam
