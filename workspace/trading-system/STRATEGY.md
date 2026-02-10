# SPOT TRADING STRATEGY — COINBASE ADVANCED
## Version 4.0 | Built by Arki (Engineer)
## Date: 2026-02-09

---

## PHILOSOPHY

> Pivot from event-based prediction markets to volatility-based spot trading. The edge comes from identifying overextended moves and mean-reversion opportunities in high-liquidity crypto pairs.

---

## 📐 MATHEMATICAL TRIGGERS

### 1. Mean Reversion (The "Rubber Band" Trade)
**Objective:** Buy when the price is significantly below its local average, expecting a snap-back.

```
Z_Score = (Price_Current - Moving_Average_20) / Std_Dev_20

Trigger (BUY): Z_Score < -2.0
Confirmation: RSI_14 < 30 and Bullish Divergence
Exit: Z_Score > 0 (Touch of the mean)
```

### 2. Trend Exhaustion (The "Top Out" Trade)
**Objective:** Sell or take profit when a trend shows signs of slowing down at extreme levels.

```
Trigger (SELL):
  1. Price > Upper Bollinger Band (2.0)
  2. RSI_14 > 70
  3. Volume_Momentum < 0 (Price rising on falling volume)

Confirmation: Bearish Engulfing Candle or 1h Trend Break
```

---

## 📐 POSITION SIZING & RISK

### Layer 1: Fractional Kelly
```
f = (p * b - q) / b / 4 (Quarter Kelly)

For spot:
  p = Estimated win probability from Analyzer (DeepSeek)
  b = (Expected_Exit - Entry) / Entry (Reward/Risk ratio)
```

### Layer 2: Volatility Scaling
```
position_size = base_size * (Target_Vol / Current_Vol)
```

---

## DECISION PIPELINE (Spot)

1.  **Market Selection:** Focus on BTC-USD, ETH_USD, SOL-USD.
2.  **Microstructure Check:** 
    *   Spread < 0.1%
    *   Liquidity Score > 5.0
3.  **Trigger Detection:**
    *   Check for Mean Reversion (Z-Score < -2)
    *   Check for Trend Exhaustion (RSI > 70 + Vol Drop)
4.  **Bayesian Update:**
    *   Update technical signals with Sentiment (ScoutGamma) and Macro (ScoutAlpha).
5.  **Analyzer Validation:**
    *   Send full context to DeepSeek V3.2 for "Second Opinion".
    *   If DeepSeek Confidence < 0.7 -> SKIP.
6.  **Execution:**
    *   `paper` mode: Log simulated buy/sell.
    *   `live` mode: Execute via Coinbase API.
