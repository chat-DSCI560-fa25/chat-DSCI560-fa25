import pandas as pd
import numpy as np

def calculate_kpis(daily_portfolio_value: list, cash_start: float):
    
    if not daily_portfolio_value:
        return {
            "total_return_pct": 0,
            "sharpe_ratio": 0,
            "max_drawdown_pct": 0,
        }

  
    equity_curve = pd.DataFrame(daily_portfolio_value, columns=['date', 'value']).set_index('date')['value']
    
   
    total_return_pct = (equity_curve.iloc[-1] / cash_start - 1) * 100

    daily_returns = equity_curve.pct_change().dropna()
    if daily_returns.std() > 0:
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown_pct = drawdown.min() * 100
    
    return {
        "total_return_pct": round(total_return_pct, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
    }