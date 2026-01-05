# src/umcp/regime/classify.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from umcp.contract import FrozenContract
from umcp.kernel import Tier1Row


Regime = Literal["Stable", "Watch", "Collapse"]


def classify_regime(row: Tier1Row, contract: FrozenContract) -> Regime:
    """
    Classify a Tier-1 row into a regime using the contract's default gates.

    Priority:
      1) Collapse if ω >= watch_omega_max
      2) Stable if all stable gates pass
      3) Otherwise Watch
    """
    omega = float(row.omega)
    F = float(row.F)
    S = float(row.S)
    C = float(row.C)

    if omega >= float(contract.watch_omega_max):
        return "Collapse"

    if (
        omega < float(contract.stable_omega_max)
        and F > float(contract.stable_F_min)
        and S < float(contract.stable_S_max)
        and C < float(contract.stable_C_max)
    ):
        return "Stable"

    return "Watch"
