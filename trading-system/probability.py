#!/usr/bin/env python3
"""
Bayesian Probability Estimation Module
Sequential updating with signal reliability tracking.
"""

import math
import json
from typing import Dict, Optional


class BayesianEstimator:
    """
    Estimates true probability using Bayesian sequential updating.
    Each signal source has a tracked reliability score that updates
    based on whether that source was correct.
    """

    def __init__(self, signal_config: Dict):
        self.reliability = dict(signal_config["initial_reliability"])
        self.ema_alpha = signal_config.get("ema_alpha", 0.05)
        self.prediction_history = []  # Track for Brier score

    def estimate(self, p_market: float, signals: Dict[str, Optional[float]]) -> float:
        """
        Estimate true probability using Bayesian sequential updating.
        
        Args:
            p_market: Current market-implied probability (0-1)
            signals: Dict of signal_source -> signal_value (0-1 probability)
                     None values are skipped.
        
        Returns:
            Posterior probability estimate (0-1)
        """
        posterior = self._clip(p_market)
        
        for source, signal_value in signals.items():
            if signal_value is None:
                continue
            
            signal_value = self._clip(signal_value)
            rel = self.reliability.get(source, 0.5)
            
            posterior = self._bayesian_update(posterior, signal_value, rel)
        
        # Store for Brier score calculation
        self.prediction_history.append({
            "p_market": p_market,
            "p_estimated": posterior,
            "signals": {k: v for k, v in signals.items() if v is not None}
        })
        
        return posterior

    def _bayesian_update(self, prior: float, signal: float, reliability: float) -> float:
        """
        Single Bayesian update step.
        
        The signal is treated as evidence that the event will occur.
        Reliability modulates how much we trust the signal.
        A perfectly reliable signal (1.0) fully updates the prior.
        A completely unreliable signal (0.0) doesn't change the prior.
        """
        # Likelihood of seeing this signal if event is true
        likelihood_true = signal * reliability + (1 - reliability) * 0.5
        
        # Likelihood of seeing this signal if event is false
        likelihood_false = (1 - signal) * reliability + (1 - reliability) * 0.5
        
        # Bayes' theorem
        numerator = prior * likelihood_true
        denominator = numerator + (1 - prior) * likelihood_false
        
        if denominator == 0:
            return prior
        
        posterior = numerator / denominator
        return self._clip(posterior)

    def update_reliability(self, trade: Dict):
        """
        After a trade closes, update signal reliability scores.
        
        Uses exponential moving average:
          new_reliability = old * (1 - alpha) + correct * alpha
        
        Where correct = 1 if signal pointed toward actual outcome, 0 otherwise.
        """
        outcome = trade.get("outcome")
        if outcome not in ("win", "loss"):
            return
        
        actual = 1.0 if outcome == "win" else 0.0
        p_bayesian = trade.get("p_bayesian", 0.5)
        side = trade.get("side", "YES")
        
        # The "correct" direction: did our estimate agree with reality?
        if side == "YES":
            our_prediction = p_bayesian
        else:
            our_prediction = 1 - p_bayesian
        
        # For each signal, check if it was pointing in the right direction
        signals = trade.get("signals_used", {})
        for source, value in signals.items():
            if source not in self.reliability:
                self.reliability[source] = 0.5
            
            if value is None:
                continue
            
            # Was this signal correct?
            if side == "YES":
                signal_correct = 1.0 if value > 0.5 else 0.0
            else:
                signal_correct = 1.0 if value < 0.5 else 0.0
            
            # Match against actual outcome
            if outcome == "win":
                correct = signal_correct  # Signal was right
            else:
                correct = 1.0 - signal_correct  # Signal was wrong
            
            # EMA update
            old = self.reliability[source]
            self.reliability[source] = old * (1 - self.ema_alpha) + correct * self.ema_alpha

    def get_brier_score(self, last_n: int = 20) -> float:
        """
        Calculate Brier score for last N predictions.
        Brier = mean((predicted - actual)^2)
        Lower is better. < 0.20 is well-calibrated.
        """
        recent = [p for p in self.prediction_history[-last_n:] if "actual" in p]
        if not recent:
            return 0.25  # No data, return neutral
        
        brier = sum((p["p_estimated"] - p["actual"]) ** 2 for p in recent) / len(recent)
        return brier

    def mark_outcome(self, actual_outcome: float):
        """Mark the most recent prediction with the actual outcome (0 or 1)."""
        if self.prediction_history:
            self.prediction_history[-1]["actual"] = actual_outcome

    def get_reliability_report(self) -> Dict[str, float]:
        """Get current reliability scores for all sources."""
        return dict(self.reliability)

    @staticmethod
    def _clip(p: float, epsilon: float = 0.001) -> float:
        """Clip probability to avoid 0 and 1 (which break Bayes)."""
        return max(epsilon, min(1 - epsilon, p))


class DeepSeekAnalyzer:
    """
    Hook for DeepSeek V3.2 for complex trade validation.
    """
    def __init__(self, secrets_path: str = "/home/openclaw/.secrets/deepseek.json"):
        with open(secrets_path) as f:
            secrets = json.load(f)
        self.api_key = secrets["api_key"]
        self.base_url = secrets.get("base_url", "https://api.deepseek.com/v1")

    def validate_trade(self, context: Dict) -> Dict:
        """
        Send trade context to DeepSeek for validation.
        """
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are a Senior Trading Quantitative Researcher. 
Validate the following trade opportunity. 

Context:
{json.dumps(context, indent=2)}

Analyze:
1. Is the entry logic sound?
2. Are there hidden risks?
3. What is your confidence score (0.0 to 1.0) for this trade?

Output JSON only with fields: 'approved' (bool), 'confidence' (float), 'reason' (string)."""

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "deepseek-chat", # Placeholder for v3.2
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            data = resp.json()
            return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            return {"approved": False, "confidence": 0, "reason": f"API Error: {str(e)}"}
