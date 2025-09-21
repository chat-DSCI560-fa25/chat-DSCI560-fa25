# Stock Portfolio Trading System

A Python-based system for algorithmic trading, robust portfolio management, and systematic strategy execution. The application provides both trend-following (Consensus Scoring Algorithm) and mean-reversion (EMA + RSI Crossover) strategies, accessible in a modular fashion.

***

## Getting Started

### 1. Clone the Repository
```bash
git clone <repo_url>
cd <repo_dir>
```

### 2. Configure Environment Variables
x
Copy the environment template and edit credentials:
```bash
cp .env.sample .env
```
Open `.env` in a text editor and fill in your MySQL credentials. The `MYSQL_HOST` should match the service name in `docker-compose.yml`.

### 3. Build and Launch Containers

```bash
docker-compose up --build -d
```

### 4. Initialize the Database

```bash
docker-compose exec app python init_db.py
```

### 5. Access the Application

- Main application: `http://localhost:5000`
- phpMyAdmin: `http://localhost:8080`

### 6. Stopping the Application

```bash
docker-compose down
```

***

## Strategy Module Structure

The trading system includes two independent strategy modules—each a stand-alone implementation:

### 1. Consensus Scoring Algorithm (`consensus.py`)
- Multi-indicator, trend-following strategy
- Combines MACD, RSI, and SMA filters
- Generates signals only when all conditions align (momentum, direction, trend)
- Buy/sell logic based on a cumulative score from all indicators

#### Usage:
- Inputs: OHLCV DataFrame
- Dependencies: pandas-ta
- Automatically standardizes column names
- Outputs: DataFrame with new `score` and `signal` columns

**Key logic:**
- Increment/decrement score for bullish/bearish indicator agreement
- Buy if score is 3 and above SMA_200; sell if score is -3

### 2. EMA + RSI Crossover Algorithm (`ema_rsi.py`)
- Mean-reversion plus short-term momentum strategy
- Look for oversold RSI (<45) and EMA_10 > EMA_30 as entry
- Exit on overbought RSI (>65)

#### Usage:
- Inputs: OHLCV DataFrame
- Dependencies: pandas-ta
- Outputs: DataFrame with new `signal` column

***

## Using the Strategies

To run a strategy, call the relevant Python module directly, or import within your workflow. Each module expects a price DataFrame and outputs trading signals. Strategies are decoupled by design and do not depend on each other, enabling independent extension and maintenance.

```python
import consensus
signals = consensus.generate_signals(df)
```

```python
import ema_rsi
signals = ema_rsi.generate_signals(df, params)
```

***

## Project Structure
```
├── consensus.py         # Trend-following strategy
├── ema_rsi.py          # EMA crossover + RSI strategy
├── main.py             # App entry point
├── ...                 # Other modules as described above
```

***

## Notes

- Each strategy module operates independently: you may use, adapt, or extend either in isolation.
- Environment setup and deployment based on Docker Compose for easy reproducibility and testing.
- Ensure accurate DB credentials and setup by editing `.env` as the first step after cloning.