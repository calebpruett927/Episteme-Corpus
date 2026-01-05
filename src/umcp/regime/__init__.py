# src/umcp/regime/__init__.py
"""
Regime classification based on Tier-1 outputs.

Default gates:
- Stable: ω < 0.038 and F > 0.90 and S < 0.15 and C < 0.14
- Watch:  0.038 ≤ ω < 0.30 (or unstable by other measures)
- Collapse: ω ≥ 0.30
"""

from .classify import Regime, classify_regime

__all__ = ["Regime", "classify_regime"]
