from __future__ import annotations
import pandas as pd
from metrics import calculate_kpis


def run_backtest(symbols: list[str], start_date: str, end_date: str, cash_start: float, price_loader, strategy_logic, strategy_params: dict):
    print("Backtest engine running...")

    #  First, Data Consolidation 
    all_dates = pd.date_range(start=start_date, end=end_date)
    prices_df = pd.DataFrame(index=all_dates)

    for symbol in symbols:
        df = price_loader(symbol, start_date, end_date)
        if not df.empty:
            temp_df = pd.DataFrame(index=df['dt'])
            temp_df[symbol] = df['close'].values
            prices_df = prices_df.join(temp_df)

    prices_df.dropna(how='all', inplace=True)
    prices_df.ffill(inplace=True)
    
    if prices_df.empty:
        print("No price data found for any symbols after processing. Exiting.")
        return {"kpis": {"portfolio_value": cash_start}, "positions": [], "trades": []}

    # The needed signal generation
    all_signals = []
    for symbol in prices_df.columns:
        symbol_data = prices_df[[symbol]].dropna().rename(columns={symbol: 'close'}).reset_index()
        symbol_signals = strategy_logic.generate_signals(symbol_data.rename(columns={'index':'dt'}), params=strategy_params)
        symbol_signals['symbol'] = symbol
        all_signals.append(symbol_signals.set_index('dt'))
    
    signals_df = pd.concat(all_signals)
    
    #Cashhh
    cash = cash_start
    positions = {symbol: 0 for symbol in symbols}
    trades = []
    daily_portfolio_value = []
    
    all_dates = prices_df.index.unique().sort_values()

    
    for date in all_dates:
       
        current_market_value = sum(positions[symbol] * prices_df.loc[date, symbol] for symbol in symbols if pd.notna(prices_df.loc[date, symbol]))
        total_value = cash + current_market_value
        daily_portfolio_value.append((date, total_value))

        if date in signals_df.index:
            signals_today = signals_df.loc[date]
            if isinstance(signals_today, pd.Series):
                signals_today = signals_today.to_frame().T

            for _, signal_row in signals_today.iterrows():
                symbol = signal_row['symbol']
                signal = signal_row['signal']
                current_price = prices_df.loc[date, symbol]

                if pd.isna(current_price): continue

                if signal == -1 and positions.get(symbol, 0) > 0:
                    shares_to_sell = positions[symbol]
                    proceeds = shares_to_sell * current_price
                    cash += proceeds
                    positions[symbol] = 0
                    trades.append({"date": date.strftime('%Y-%m-%d'), "symbol": symbol, "side": "SELL", "qty": shares_to_sell, "price": current_price})

 
                elif signal == 1:
                   
                    base_investment = total_value * 0.10

                    
                    current_rsi = signal_row['rsi_14']


                    conviction_multiplier = 1.0
                    if current_rsi > 50:
                       
                        bonus = min((current_rsi - 50) / 20, 1.0)
                        conviction_multiplier += bonus

                   
                    investment_amount = base_investment * conviction_multiplier
                    
                    if cash >= investment_amount:
                        shares_to_buy = int(investment_amount / current_price)
                        cost = shares_to_buy * current_price
                        if shares_to_buy > 0:
                            cash -= cost
                            positions[symbol] += shares_to_buy
                            trades.append({"date": date.strftime('%Y-%m-%d'), "symbol": symbol, "side": "BUY", "qty": shares_to_buy, "price": current_price})
    
    # Post-Backtest Calculations 
    final_portfolio_value = daily_portfolio_value[-1][1] if daily_portfolio_value else cash_start
    total_pnl = final_portfolio_value - cash_start
    
    
    #advanced_kpis = calculate_kpis(daily_portfolio_value, cash_start)
    advanced_kpis = calculate_kpis(daily_portfolio_value, cash_start, trades)

    final_positions = []
    last_prices = prices_df.iloc[-1]
    for symbol, qty in positions.items():
        if qty > 0 and symbol in last_prices:
            final_positions.append({"symbol": symbol, "qty": qty, "last": last_prices[symbol], "avg_cost": 0, "unrealized": 0})

    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")

    
    all_kpis = {
    "portfolio_value": round(final_portfolio_value, 2),
    "total_pnl": round(total_pnl, 2),
    "return_pct": advanced_kpis["total_return_pct"],
    "cagr_pct": advanced_kpis["cagr_pct"],
    "sharpe_ratio": advanced_kpis["sharpe_ratio"],
    "sortino_ratio": advanced_kpis["sortino_ratio"],
    "max_drawdown_pct": advanced_kpis["max_drawdown_pct"],
    "calmar_ratio": advanced_kpis["calmar_ratio"],
    "profit_factor": advanced_kpis["profit_factor"],
    "win_rate_pct": advanced_kpis["win_rate_pct"],
    "avg_win_loss_ratio": advanced_kpis["avg_win_loss_ratio"],
    }

    return { "kpis": all_kpis, "positions": final_positions, "trades": trades }