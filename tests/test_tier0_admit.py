import numpy as np

from umcp.contract import FrozenContract
from umcp.tier0.admit import admit_trace


def test_admit_trace_clips_and_flags_oor():
    contract = FrozenContract(a=0.0, b=1.0)

    raw = np.array(
        [
            [-0.1, 0.5, 1.2],
            [0.2, 0.3, 0.4],
        ],
        dtype=float,
    )

    admitted = admit_trace(raw, contract)

    # Clipped
    assert admitted.psi.min() >= 0.0
    assert admitted.psi.max() <= 1.0

    # Flags OOR where raw was outside [0,1]
    assert admitted.oor_mask.shape == raw.shape
    assert admitted.oor_mask[0, 0] is True
    assert admitted.oor_mask[0, 2] is True
    assert admitted.oor_mask[1, :].any() is False
