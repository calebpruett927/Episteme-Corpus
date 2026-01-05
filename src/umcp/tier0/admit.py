# src/umcp/tier0/admit.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

from umcp.contract import FrozenContract


@dataclass(frozen=True, slots=True)
class AdmittedTrace:
    """
    Output of Tier-0 admission.

    psi: admitted trace Ψ(t) in [a,b]^n
    oor_mask: boolean mask of where raw input was out-of-range
    """
    psi: np.ndarray
    oor_mask: np.ndarray


def admit_trace(raw: np.ndarray, contract: FrozenContract) -> AdmittedTrace:
    """
    Admit a raw trace to Ψ(t) ∈ [a,b]^n under the frozen contract.

    face=pre_clip + oor=clip_and_flag:
      - clip raw to [a,b]
      - flag out-of-range entries in oor_mask
    """
    x = np.asarray(raw, dtype=float)
    if x.ndim != 2:
        raise ValueError(f"raw trace must be 2D array shaped (T,n); got shape={x.shape}")

    a, b = contract.a, contract.b
    oor_mask = (x < a) | (x > b)

    if contract.face != "pre_clip":
        raise ValueError(f"unsupported face policy: {contract.face}")
    if contract.oor != "clip_and_flag":
        raise ValueError(f"unsupported OOR policy: {contract.oor}")

    psi = np.clip(x, a, b)
    return AdmittedTrace(psi=psi, oor_mask=oor_mask)
