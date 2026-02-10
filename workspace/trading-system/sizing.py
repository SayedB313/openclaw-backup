#!/usr/bin/env python3
"""
Position Sizing Module
Quarter-Kelly with volatility adjustment and tier caps.
"""

import math
from typing import Dict


class PositionSizer:
    """
    Calculates position sizes using fractional Kelly Criterion
    with volatility adjustment and hour-tier caps.
    """

    def __init__(self, sizing_config: Dict, time_config: Dict):
        self.kelly_fraction = sizing_config["kelly_fraction"]  # 0.25 = quarter-Kelly
        self.first_50_cap = sizing_config["first_50_trades_cap"]
        self.winning_cap = sizing_config["winning_hour_cap"]
        self.learning_cap = sizing_config["learning_hour_cap"]
        self.time_config = time_config

    def calculate(
        self,
        p_estimated: float,
        payout_ratio: float,
        hour_tier: str,
        portfolio_value: float,
        trade_count: int,
        volatility_ratio: float = 1.0
    ) -> Dict:
        """
        Calculate position size.
        
        Args:
            p_estimated: Our estimated probability of winning (0-1)
            payout_ratio: Win amount / Lose amount (b in Kelly formula)
            hour_tier: "winning" or "learning"
            portfolio_value: Current portfolio value
            trade_count: Total trades taken so far
            volatility_ratio: current_vol / median_vol (for adjustment)
        
        Returns:
            Dict with size_usd, size_pct, kelly details
        """
        # ─── Full Kelly ───
        p = max(0.01, min(0.99, p_estimated))
        q = 1 - p
        b = max(0.01, payout_ratio)
        
        full_kelly = (p * b - q) / b
        
        # If Kelly is negative, we have no edge
        if full_kelly <= 0:
            return {
                "size_usd": 0,
                "size_pct": 0,
                "full_kelly": full_kelly,
                "fractional_kelly": 0,
                "reason": "Negative Kelly — no edge"
            }
        
        # ─── Fractional Kelly ───
        frac_kelly = full_kelly * self.kelly_fraction
        
        # ─── Volatility Adjustment ───
        # In volatile markets, reduce size
        if volatility_ratio > 2.0:
            vol_adj = 0.5  # Half size in volatile regime
        elif volatility_ratio > 1.5:
            vol_adj = 0.75
        else:
            vol_adj = 1.0
        
        adjusted_kelly = frac_kelly * vol_adj
        
        # ─── Tier Caps ───
        if trade_count < 50:
            tier_cap = self.first_50_cap  # 2% for first 50 trades
        elif hour_tier == "winning":
            tier_cap = self.winning_cap  # 10%
        elif hour_tier == "learning":
            tier_cap = self.learning_cap  # 3%
        else:
            tier_cap = 0  # Danger hours
        
        final_pct = min(adjusted_kelly, tier_cap)
        final_usd = portfolio_value * final_pct
        
        return {
            "size_usd": round(final_usd, 2),
            "size_pct": final_pct,
            "full_kelly": round(full_kelly, 4),
            "fractional_kelly": round(frac_kelly, 4),
            "vol_adjusted": round(adjusted_kelly, 4),
            "tier_cap": tier_cap,
            "vol_adjustment": vol_adj,
            "hour_tier": hour_tier
        }

    def check_portfolio_heat(
        self,
        proposed_size: float,
        open_positions: list,
        portfolio_value: float,
        hour_tier: str
    ) -> Dict:
        """Check if adding this position would exceed total exposure limits."""
        current_exposure = sum(abs(p.get("size_usd", 0)) for p in open_positions)
        new_exposure = current_exposure + proposed_size
        exposure_pct = new_exposure / portfolio_value if portfolio_value > 0 else 1.0
        
        if hour_tier == "winning":
            max_exposure = 0.25  # 25% total
        else:
            max_exposure = 0.10  # 10% total
        
        return {
            "current_exposure": current_exposure,
            "new_exposure": new_exposure,
            "exposure_pct": exposure_pct,
            "max_exposure": max_exposure,
            "approved": exposure_pct <= max_exposure,
            "reason": f"Exposure {exposure_pct:.0%} {'<=' if exposure_pct <= max_exposure else '>'} {max_exposure:.0%} limit"
        }
