import math
import numpy as np

from umcp.contract import FrozenContract
from umcp.kernel import compute_tier1_series


def test_tier1_identity_ic_equals_exp_kappa():
    contract = FrozenContract()

    # A simple admitted trace Ψ(t) ∈ [0,1]^n
    psi = np.array(
        [
            [0.10, 0.20, 0.30],
            [0.11, 0.19, 0.31],
            [0.12, 0.18, 0.32],
            [0.12, 0.18, 0.32],  # explicit repeat to allow a finite return lag
        ],
        dtype=float,
    )

    rows = compute_tier1_series(psi, contract)

    assert len(rows) == psi.shape[0]

    for row in rows:
        # Canonical Tier-1 identity check
        assert math.isclose(row.IC, math.exp(row.kappa), rel_tol=0.0, abs_tol=1e-12)
        # Sanity: IC in (0,1], κ <= 0 by construction in this minimal kernel
        assert 0.0 < row.IC <= 1.0
        assert row.kappa <= 1e-12  # allow tiny numeric noise

        # Fidelity is clipped into [0,1]
        assert 0.0 <= row.F <= 1.0
