# Model 1: Optimized SMA + RSI Trading Strategy

## Overview
This repository contains a **rule‑based trading system** that combines two popular technical indicators — **Simple Moving Average (SMA)** and **Relative Strength Index (RSI)** — to generate buy and sell signals for one or more stocks.

The model:
- Simulates a **mock trading environment** with cash and positions.
- Executes trades based on indicator signals.
- Tracks portfolio value over time.
- Calculates key performance metrics.

---

### 3. Trade Execution
- On a **buy signal**, the model allocates available cash equally across all tickers generating a signal that day.
- On a **sell signal**, the model liquidates the position in that ticker.
- Portfolio value is updated daily to reflect cash and the market value of all open positions.

---

### 4. Risk Management
While the base model does not include stop‑loss or take‑profit orders, it inherently manages risk by:
- Only entering trades in the direction of the prevailing trend.
- Avoiding overbought entries and oversold exits.
- Staying in cash when no valid signals are present.

You can extend the model with:
- **ATR‑based stops** for volatility‑adjusted exits.
- **Position sizing** based on volatility or fixed risk per trade.

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

## Model 2

# Stock Portfolio Trading System

A comprehensive Python-based algorithmic trading system for portfolio management, market data acquisition, and systematic trading strategy execution. This system combines institutional-grade portfolio management with advanced quantitative analysis, featuring database persistence, real-time data processing, technical indicator computation, and systematic trading execution.

## �� Key Features

### Advanced Trading Strategy
- **Multi-factor signal generation** combining trend following, momentum analysis, and mean reversion
- **Sophisticated risk management** with transaction costs, position sizing, and drawdown control
- **Real-time performance analytics** with institutional-grade metrics
- **User-configurable parameters** for strategy customization (MA windows, RSI thresholds, transaction costs)

### Portfolio Management
- **Complete CRUD operations** for portfolios and stocks
- **Portfolio deletion** with smart data cleanup (preserves shared price data)
- **Multi-portfolio support** with isolated management
- **Stock universe management** with easy add/remove functionality

### Data Infrastructure
- **MySQL database backend** with optimized schema for time-series data
- **Automated data fetching** via yfinance API with error handling
- **Data preprocessing pipeline** with 15+ technical indicators
- **Efficient data storage** with upsert operations and conflict resolution

### User Experience
- **Unified command-line interface** - everything accessible via `python main.py`
- **Interactive prompts** with input validation and defaults
- **Comprehensive output** including CSV results and performance charts
- **Real-time feedback** with progress tracking and error handling

---

## Project Structure

```
├── main.py                    # 🎯 Main application entry point with unified menu
├── portfolio.py               # 📁 Portfolio management (create, list, delete)
├── stocks.py                  # 📈 Stock management (add, remove from portfolios)
├── prices.py                  # 💰 Market data fetching and storage
├── preprocessing.py           # 🔧 Technical indicator computation & feature engineering
├── simple_trading_strategy.py # 🤖 Advanced algorithmic trading strategy
├── db_config.py              # 🗄️ Database connection configuration
├── init_db.py                # 📊 Database schema initialization
├── requirements.txt          # 📦 Python dependencies
├── readme.md                 # 📚 Project documentation
└── .venv/                    # 🐍 Virtual environment
```

### Database Schema
- **`portfolios`** - Portfolio metadata with auto-incrementing IDs
- **`portfolio_stocks`** - Many-to-many relationship between portfolios and stocks
- **`stock_prices`** - Historical OHLCV data with unique constraints

---

## Quick Start Guide

### 1. Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database schema
python init_db.py
```

### 2. Portfolio Setup
```bash
# Launch main application
python main.py

# Use menu options to:
# 1) Create a new portfolio
# 2) Add stocks to your portfolio (e.g., AAPL, MSFT, GOOGL, AMZN, TSLA)
# 3) Fetch historical price data for your portfolio
```

### 3. Execute Trading Strategy
```bash
# Run the complete trading workflow via main menu
python main.py
# Choose option 5: "Perform Trade (Simple Strategy)"

# Or run strategy directly
python simple_trading_strategy.py
```

**Input Parameters:**
- Portfolio ID to trade
- Date range (e.g., 2015-01-01 to 2016-12-31)
- Initial cash amount
- Transaction costs (basis points per side)
- Advanced parameters (MA window, RSI thresholds)

### 4. Results Analysis
- **CSV Output**: `simple_strategy_results.csv` - Complete trading history with signals
- **Performance Chart**: `simple_strategy_performance.png` - Equity curve and drawdown analysis
- **Console Metrics**: Comprehensive performance summary with interpretation

---

## Strategy Performance

### Live Example Results
```
Portfolio ID: 5 | Period: 2015-01-01 to 2016-12-31 | Initial: $1,000
Final Capital: $1,121.59 | Total Return: 12.16% | Annual Return: 5.91%
Sharpe Ratio: 0.709 | Max Drawdown: 8.57% | Executed Trades: 617
```

### Performance Interpretation
- **Sharpe Ratio > 0.5**: Good risk-adjusted returns
- **Low Drawdown**: Excellent risk control (< 10%)
- **Consistent Performance**: 50%+ win rate with systematic execution
- **Transaction Cost Aware**: Realistic returns including execution costs

---

## Advanced Configuration

### Database Configuration (`db_config.py`)
```python
DB_SETTINGS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "stock_data",
}
```

### Strategy Parameters
- **MA Window**: 5, 10, or 20 days (trend identification)
- **RSI Buy Max**: 70, 75, or 80 (momentum filter)
- **RSI Sell Min**: Auto-calculated as buy_max + 5 (exit trigger)
- **Transaction Costs**: 0-20 basis points per side (realistic execution)

### Technical Indicators Available
- Moving Averages (5, 20 day)
- RSI (14-period momentum)
- MACD (trend following)
- Bollinger Bands (volatility)
- ATR (volatility measurement)
- Volume ratios and momentum indicators

---

## Database Setup

### MySQL Installation & Configuration
1. **Install MySQL** and ensure server is running
2. **Create database and user**:
   ```sql
   CREATE DATABASE stock_data;
   CREATE USER 'root'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON stock_data.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. **Run initialization**:
   ```bash
   python init_db.py
   ```

---

## Menu System

### Main Menu (`python main.py`)
```
####################################
 Stock Portfolio Manager—  Main Menu
####################################
1) Portfolio manager          # Create, list, delete portfolios
2) Stocks manager            # Add/remove stocks from portfolios
3) Fetch & store prices      # Download historical market data
4) Query stored prices       # View stored price history
5) Perform Trade (Simple Strategy)  # Execute trading strategy
0) Exit
```

### Portfolio Manager (Option 1)
```
**********************
 Portfolio Manager
**********************
1) Create a brand new portfolio
2) List existing portfolios
3) Delete a portfolio        # ⚠️ NEW: Smart deletion with data cleanup
0) Exit
```

---

## Trading Strategy Details

### Signal Generation Logic
1. **Trend Filter**: Price above short-term moving average
2. **Momentum Confirmation**: Positive 5-day momentum
3. **Overbought Protection**: RSI below buy threshold
4. **Exit Triggers**: Trend break OR momentum loss OR extreme overvaluation

### Risk Management Features
- **Equal allocation** across portfolio stocks
- **Transaction cost modeling** (configurable basis points)
- **Position size limits** based on portfolio value
- **Automatic rebalancing** on signal changes
- **Real-time P&L tracking** with equity curve generation

### Performance Metrics Calculated
- **Total Return & CAGR**: Compound annual growth rate
- **Sharpe Ratio**: Risk-adjusted return measurement
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Calmar Ratio**: CAGR divided by maximum drawdown
- **Executed Trades**: Actual buy/sell transaction count

---

## Dependencies

### Core Requirements (`requirements.txt`)
```
pandas>=1.5.0
numpy>=1.21.0
yfinance>=0.2.0
mysql-connector-python>=8.0.0
matplotlib>=3.5.0
scikit-learn>=1.1.0
```

### Development Environment
- **Python**: 3.8+ recommended
- **MySQL**: 8.0+ for optimal performance
- **Virtual Environment**: Isolated dependency management
- **Operating System**: Cross-platform (Windows, macOS, Linux)

---

## Troubleshooting

### Common Issues & Solutions

**Database Connection Failed**
```bash
# Check MySQL service status
brew services start mysql  # macOS
sudo service mysql start   # Linux

# Verify credentials in db_config.py
```

**Module Import Errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**No Price Data Available**
```bash
# Ensure internet connection for yfinance
# Check stock symbols are valid (e.g., AAPL, not Apple)
# Verify date ranges are not weekends/holidays
```

**Strategy Performance Issues**
```bash
# Try different parameter combinations
# Ensure sufficient historical data (>100 days recommended)
# Check for data quality issues in price feeds
```

---

## Additional Resources

### Learning Resources
- **Technical Analysis**: Understanding RSI, MACD, Moving Averages
- **Risk Management**: Position sizing and portfolio theory
- **Python Finance**: pandas, numpy for quantitative analysis
- **Database Design**: MySQL optimization for time-series data

### Future Enhancements
- **Machine Learning Integration**: ML-based signal enhancement
- **Real-time Trading**: Live market data and order execution
- **Advanced Strategies**: Mean reversion, arbitrage, multi-asset
- **Web Interface**: Flask/Django-based portfolio management UI
- **API Integration**: RESTful API for external system connectivity

---

## License

This project is designed for educational and research purposes. Please ensure compliance with financial regulations if used for actual trading.

## �� Contributing

Feel free to fork this repository and submit pull requests for improvements. Key areas for contribution:
- Additional technical indicators
- Alternative trading strategies
- Performance optimizations
- Documentation improvements
- Test coverage expansion

---

**Happy Trading! **
