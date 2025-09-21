import pandas as pd
import numpy as np

def calculate_kpis(daily_portfolio_value: list, cash_start: float, trades: list):
    
    if not daily_portfolio_value:
        return {
            "total_return_pct": 0, "cagr_pct": 0, "sharpe_ratio": 0,
            "sortino_ratio": 0, "max_drawdown_pct": 0, "calmar_ratio": 0,
            "profit_factor": 0, "win_rate_pct": 0, "avg_win_loss_ratio": 0,
        }

    # --- Portfolio-Level Metrics ---
    equity_curve = pd.DataFrame(daily_portfolio_value, columns=['date', 'value']).set_index('date')['value']
    
    total_return_pct = (equity_curve.iloc[-1] / cash_start - 1) * 100

    # CAGR
    days = (equity_curve.index[-1] - equity_curve.index[0]).days
    years = days / 365.25
    cagr_pct = ((equity_curve.iloc[-1] / cash_start) ** (1 / years) - 1) * 100 if years > 0 else 0

    # Sharpe & Sortino
    daily_returns = equity_curve.pct_change().dropna()
    sharpe_ratio = 0.0
    sortino_ratio = 0.0

    if daily_returns.std() > 0:
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        
        negative_returns = daily_returns[daily_returns < 0]
        downside_std = negative_returns.std()
        if downside_std > 0:
            sortino_ratio = (daily_returns.mean() / downside_std) * np.sqrt(252)

    # Drawdown & Calmar
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown_pct = drawdown.min() * 100
    calmar_ratio = (cagr_pct / 100) / abs(max_drawdown_pct / 100) if max_drawdown_pct != 0 else 0

    
    profit_factor = 0
    win_rate_pct = 0
    avg_win_loss_ratio = 0

    if trades:
        # simplified P&L calculation 
        trades_df = pd.DataFrame(trades)
        pnl_per_symbol = {}
        for symbol in trades_df['symbol'].unique():
            buys = trades_df[(trades_df['symbol'] == symbol) & (trades_df['side'] == 'BUY')]
            sells = trades_df[(trades_df['symbol'] == symbol) & (trades_df['side'] == 'SELL')]
            
            if not sells.empty:
                total_cost = (buys['qty'] * buys['price']).sum()
                total_proceeds = (sells['qty'] * sells['price']).sum()
                pnl_per_symbol[symbol] = total_proceeds - total_cost

        wins = [pnl for pnl in pnl_per_symbol.values() if pnl > 0]
        losses = [pnl for pnl in pnl_per_symbol.values() if pnl < 0]

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        
        if len(wins) + len(losses) > 0:
            win_rate_pct = (len(wins) / (len(wins) + len(losses))) * 100

        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 0
        if avg_loss > 0:
            avg_win_loss_ratio = avg_win / avg_loss

    return {
        "total_return_pct": round(total_return_pct, 2), "cagr_pct": round(cagr_pct, 2),
        "sharpe_ratio": round(sharpe_ratio, 2), "sortino_ratio": round(sortino_ratio, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2), "calmar_ratio": round(calmar_ratio, 2),
        "profit_factor": round(profit_factor, 2), "win_rate_pct": round(win_rate_pct, 2),
        "avg_win_loss_ratio": round(avg_win_loss_ratio, 2),
    }