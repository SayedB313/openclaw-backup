#!/usr/bin/env python3
"""
Risk Management Module
Circuit breakers, drawdown control, daily limits.
"""

import math
import time
from typing import Dict, List
from datetime import datetime, timezone


class RiskManager:
    """
    Enforces risk limits and circuit breakers.
    This is the last line of defense before capital destruction.
    """

    def __init__(self, risk_config: Dict):
        self.config = risk_config
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.consecutive_losses = 0
        self.last_reset_day = None
        self.last_reset_week = None
        self.portfolio_history = []  # For drawdown tracking
        self.pause_until = 0  # Unix timestamp
        self.alerts = []

    def check_trade(
        self,
        position_size: float,
        portfolio_value: float,
        open_positions: List[Dict],
        hour_tier: str
    ) -> Dict:
        """
        Pre-trade risk check. Must pass ALL checks.
        """
        self._maybe_reset_daily()
        
        # Check 1: Are we paused?
        if time.time() < self.pause_until:
            remaining = (self.pause_until - time.time()) / 3600
            return {
                "approved": False,
                "reason": f"System paused ({remaining:.1f}h remaining after consecutive losses)"
            }
        
        # Check 2: Daily loss limit
        max_loss_today = portfolio_value * self.config["max_daily_loss_pct"]
        potential_loss = position_size  # Worst case = lose entire position
        
        if (abs(self.daily_pnl) + potential_loss) > max_loss_today and self.daily_pnl < 0:
            return {
                "approved": False,
                "reason": f"Daily loss limit: already lost ${abs(self.daily_pnl):.2f}, max ${max_loss_today:.2f}"
            }
        
        # Check 3: Weekly loss limit
        max_loss_week = portfolio_value * self.config["max_weekly_loss_pct"]
        if abs(self.weekly_pnl) > max_loss_week and self.weekly_pnl < 0:
            return {
                "approved": False,
                "reason": f"Weekly loss limit hit: ${abs(self.weekly_pnl):.2f} > ${max_loss_week:.2f}"
            }
        
        # Check 4: Drawdown check
        drawdown = self._calculate_drawdown(portfolio_value)
        if drawdown > self.config["max_drawdown_stop_pct"]:
            return {
                "approved": False,
                "reason": f"Drawdown {drawdown:.1%} > {self.config['max_drawdown_stop_pct']:.0%} — STOP"
            }
        
        if drawdown > self.config["max_drawdown_warning_pct"]:
            # Allow but at reduced size (Learning tier caps only)
            if hour_tier == "winning":
                return {
                    "approved": False,
                    "reason": f"Drawdown {drawdown:.1%} — reduced to Learning size only"
                }
        
        # Check 5: Portfolio heat
        current_exposure = sum(abs(p.get("size_usd", 0)) for p in open_positions)
        max_exp = 0.25 if hour_tier == "winning" else 0.10
        new_exposure = (current_exposure + position_size) / portfolio_value if portfolio_value > 0 else 1
        
        if new_exposure > max_exp:
            return {
                "approved": False,
                "reason": f"Total exposure {new_exposure:.0%} would exceed {max_exp:.0%}"
            }
        
        return {
            "approved": True,
            "daily_pnl": self.daily_pnl,
            "drawdown": drawdown,
            "exposure": new_exposure,
            "consecutive_losses": self.consecutive_losses
        }

    def record_trade_result(self, pnl: float, portfolio_value: float):
        """Record trade result and update all risk counters."""
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        self.portfolio_history.append({
            "timestamp": time.time(),
            "value": portfolio_value
        })
        
        if pnl < 0:
            self.consecutive_losses += 1
            self._check_consecutive_loss_breaker()
        else:
            self.consecutive_losses = 0
        
        # Drawdown alerts
        drawdown = self._calculate_drawdown(portfolio_value)
        if drawdown > self.config["max_drawdown_alert_pct"]:
            self.alerts.append({
                "type": "CRITICAL_DRAWDOWN",
                "message": f"Drawdown {drawdown:.1%} exceeds {self.config['max_drawdown_alert_pct']:.0%} — ALERT B",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    def _check_consecutive_loss_breaker(self):
        """Exponential backoff pause after consecutive losses."""
        base = self.config["consecutive_loss_pause_base"]  # 3
        if self.consecutive_losses >= base:
            pause_hours = 2 ** (self.consecutive_losses - base + 1)
            self.pause_until = time.time() + (pause_hours * 3600)
            self.alerts.append({
                "type": "CONSECUTIVE_LOSS_PAUSE",
                "message": f"{self.consecutive_losses} consecutive losses — paused for {pause_hours}h",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    def _calculate_drawdown(self, current_value: float) -> float:
        """Calculate drawdown from rolling 7-day max."""
        if not self.portfolio_history:
            return 0.0
        
        week_ago = time.time() - (7 * 24 * 3600)
        recent = [h["value"] for h in self.portfolio_history if h["timestamp"] > week_ago]
        recent.append(current_value)
        
        peak = max(recent)
        drawdown = (peak - current_value) / peak if peak > 0 else 0
        return drawdown

    def _maybe_reset_daily(self):
        """Reset daily counters at midnight."""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_reset_day != today:
            self.daily_pnl = 0.0
            self.last_reset_day = today
        
        # Weekly reset on Monday
        weekday = datetime.now().weekday()
        week_key = datetime.now().strftime("%Y-W%W")
        if self.last_reset_week != week_key:
            self.weekly_pnl = 0.0
            self.last_reset_week = week_key

    def get_alerts(self) -> List[Dict]:
        """Get and clear pending alerts."""
        alerts = list(self.alerts)
        self.alerts.clear()
        return alerts

    def get_status(self) -> Dict:
        """Get current risk status."""
        return {
            "daily_pnl": self.daily_pnl,
            "weekly_pnl": self.weekly_pnl,
            "consecutive_losses": self.consecutive_losses,
            "paused": time.time() < self.pause_until,
            "pause_remaining_h": max(0, (self.pause_until - time.time()) / 3600),
            "drawdown": self._calculate_drawdown(
                self.portfolio_history[-1]["value"] if self.portfolio_history else 0
            )
        }
