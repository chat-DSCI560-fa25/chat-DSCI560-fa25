# Model 1: Optimized SMA + RSI Trading Strategy

## Overview
This repository contains a **rule‑based trading system** that combines two popular technical indicators — **Simple Moving Average (SMA)** and **Relative Strength Index (RSI)** — to generate buy and sell signals for one or more stocks.

The model:
- Simulates a **mock trading environment** with cash and positions.
- Executes trades based on indicator signals.
- Tracks portfolio value over time.
- Calculates key performance metrics.

---

## Inputs

| Parameter | Description |
|-----------|-------------|
| **Price Data** | Historical daily closing prices for selected stock(s). |
| **short_w** | Short‑term SMA window length (days). |
| **long_w** | Long‑term SMA window length (days). |
| **rsi_low** | RSI threshold for oversold condition (buy zone). |
| **rsi_high** | RSI threshold for overbought condition (sell zone). |
| **initial_cash** | Starting capital for the simulation. |
| **tickers** | List of stock symbols in the portfolio. |
| **risk_free_rate** | Annualized risk‑free rate for Sharpe ratio calculation. |

---

## Outputs

| Output | Description |
|--------|-------------|
| **Best Parameters** | SMA and RSI settings with the highest performance. |
| **Total Portfolio Value** | Final value of cash + open positions. |
| **Total Profit/Loss** | Final portfolio value − starting cash. |
| **Total Return (%)** | Percentage gain/loss over the backtest period. |
| **Annualized Return (%)** | Return adjusted to a yearly rate. |
| **Sharpe Ratio** | Risk‑adjusted return metric. |
| **Trade Log** | Record of all executed trades. |
| **Equity Curve** | Portfolio value over time. |
| **Trading Plan** | Plain‑English buy/sell/hold rules for the best parameters. |

---

## Strategy Logic

### Indicators
- **SMA (Simple Moving Average)**  
  - Short SMA reacts quickly to price changes.  
  - Long SMA smooths out long‑term trends.
- **RSI (Relative Strength Index)**  
  - Measures momentum on a 0–100 scale.  
  - Low RSI (< `rsi_low`) = oversold.  
  - High RSI (> `rsi_high`) = overbought.

### Signal Rules
- **Buy**:  
  - Short SMA > Long SMA  
  - AND RSI < `rsi_low`
- **Sell**:  
  - Short SMA < Long SMA  
  - OR RSI > `rsi_high`
- **Hold**:  
  - Neither buy nor sell conditions are met.

---

## Example Trading Plan

For parameters:
- Short SMA: `20`
- Long SMA: `50`
- RSI Low: `35`
- RSI High: `60`


---

## Performance Metrics

The model reports:
- **Total Portfolio Value**: Cash + market value of open positions.
- **Total Profit/Loss**: Final value − initial cash.
- **Total Return (%)**: Overall percentage change.
- **Annualized Return (%)**: Return normalized to a yearly rate.
- **Sharpe Ratio**: Risk‑adjusted performance.
