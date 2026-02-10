#!/usr/bin/env python3
"""
Trade Journal Module
Logging, forensics, and performance analytics.
The consequence loop lives here.
"""

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone


class TradeJournal:
    """
    Every trade gets logged. Every outcome gets analyzed.
    This is the memory that prevents repeated mistakes.
    """

    def __init__(self, journal_path: str = "data/trades.jsonl"):
        self.path = Path(journal_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trades: List[Dict] = []
        self._load()

    def _load(self):
        """Load existing trades from disk."""
        if self.path.exists():
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            self.trades.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

    def _append(self, record: Dict):
        """Append a record to the journal file."""
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def log_entry(self, trade: Dict):
        """Log a trade entry."""
        record = {
            "type": "ENTRY",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **trade
        }
        self.trades.append(record)
        self._append(record)

    def log_close(self, trade: Dict):
        """Log a trade close with full forensics."""
        record = {
            "type": "CLOSE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **trade
        }
        self.trades.append(record)
        self._append(record)

    def get_recent_trades(self, n: int = 10) -> List[Dict]:
        """Get last N closed trades."""
        closed = [t for t in self.trades if t.get("type") == "CLOSE"]
        return closed[-n:]

    def get_similar_trades(self, category: str, event_type: str) -> List[Dict]:
        """Find trades in similar markets."""
        return [
            t for t in self.trades
            if t.get("type") == "CLOSE"
            and (t.get("category") == category or t.get("event_type") == event_type)
        ]

    def get_stats(self) -> Dict:
        """Calculate comprehensive trading statistics."""
        closed = [t for t in self.trades if t.get("type") == "CLOSE"]
        
        if not closed:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "sharpe": 0,
                "brier_score": 0.25,
                "max_drawdown": 0,
                "total_pnl": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0
            }
        
        wins = [t for t in closed if t.get("outcome") == "win"]
        losses = [t for t in closed if t.get("outcome") == "loss"]
        
        total = len(closed)
        win_rate = len(wins) / total if total > 0 else 0
        
        # P&L
        pnls = [t.get("pnl_usd", 0) for t in closed]
        total_pnl = sum(pnls)
        
        avg_win = sum(t.get("pnl_usd", 0) for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.get("pnl_usd", 0) for t in losses) / len(losses) if losses else 0
        
        gross_profit = sum(t.get("pnl_usd", 0) for t in wins)
        gross_loss = abs(sum(t.get("pnl_usd", 0) for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Sharpe ratio (annualized)
        if len(pnls) > 1:
            mean_pnl = sum(pnls) / len(pnls)
            std_pnl = math.sqrt(sum((p - mean_pnl) ** 2 for p in pnls) / (len(pnls) - 1))
            sharpe = (mean_pnl / std_pnl) * math.sqrt(365) if std_pnl > 0 else 0
        else:
            sharpe = 0
        
        # Max drawdown
        running = 0
        peak = 0
        max_dd = 0
        for p in pnls:
            running += p
            peak = max(peak, running)
            dd = (peak - running) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        # Brier score (if probability data available)
        predictions = [(t.get("p_bayesian", 0.5), 1.0 if t["outcome"] == "win" else 0.0)
                       for t in closed if "p_bayesian" in t]
        brier = sum((p - a) ** 2 for p, a in predictions) / len(predictions) if predictions else 0.25
        
        # Win rate by hour tier
        tier_stats = {}
        for tier in ["winning", "learning"]:
            tier_trades = [t for t in closed if t.get("hour_tier") == tier]
            if tier_trades:
                tier_wins = sum(1 for t in tier_trades if t["outcome"] == "win")
                tier_stats[tier] = {
                    "trades": len(tier_trades),
                    "win_rate": tier_wins / len(tier_trades),
                    "pnl": sum(t.get("pnl_usd", 0) for t in tier_trades)
                }
        
        return {
            "total_trades": total,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe": sharpe,
            "max_drawdown": max_dd,
            "brier_score": brier,
            "tier_stats": tier_stats
        }

    def get_consequence_context(self, market_category: str = "") -> str:
        """
        Generate consequence context for the conscience layer.
        This is loaded BEFORE every trade decision to make past failures visible.
        
        Per LaylaEleira: "Make the cost of past failures visible before the next output."
        """
        closed = self.get_recent_trades(20)
        if not closed:
            return "No trade history yet. First trades — extra caution."
        
        losses = [t for t in closed if t.get("outcome") == "loss"]
        
        if not losses:
            return f"Last {len(closed)} trades: all wins. Stay disciplined."
        
        context_lines = [
            f"⚠️ CONSEQUENCE CONTEXT ({len(losses)}/{len(closed)} recent losses):"
        ]
        
        for loss in losses[-3:]:  # Show last 3 losses
            context_lines.append(
                f"  • Lost ${abs(loss.get('pnl_usd', 0)):.2f} on {loss.get('market', '?')} "
                f"(dissonance={loss.get('dissonance', '?')}, {loss.get('hour_tier', '?')} hour)"
            )
        
        # Similar market warning
        if market_category:
            similar_losses = [
                t for t in closed
                if t.get("outcome") == "loss" and t.get("category") == market_category
            ]
            if similar_losses:
                context_lines.append(
                    f"  ⚠️ {len(similar_losses)} losses in similar '{market_category}' markets recently"
                )
        
        return "\n".join(context_lines)

    def export_csv(self, path: str = "data/trades_export.csv"):
        """Export trades to CSV for analysis."""
        import csv
        closed = [t for t in self.trades if t.get("type") == "CLOSE"]
        if not closed:
            return
        
        fields = ["trade_id", "market", "side", "entry_price", "exit_price",
                   "size_usd", "pnl_usd", "pnl_pct", "outcome", "hour_tier",
                   "regime", "p_bayesian", "conviction", "timestamp", "closed_at"]
        
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(closed)
