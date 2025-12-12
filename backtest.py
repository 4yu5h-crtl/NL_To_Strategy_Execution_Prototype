import pandas as pd
from utils import indicators

def run_backtest(df, indicator_code, entry_code, exit_code, initial_capital=10000.0):
    """
    Runs a backtest for a given strategy.

    Args:
        df (pd.DataFrame): DataFrame with historical price data (Date, open, high, low, close, volume).
        indicator_code (str): The Python code to generate indicator columns.
        entry_code (str): The pandas condition for entry signals.
        exit_code (str): The pandas condition for exit signals.
        initial_capital (float): The starting capital for the backtest.

    Returns:
        A dictionary containing backtest performance metrics.
    """
    # IMPORTANT: Using exec() is a security risk if the code is not from a trusted source.
    # In this self-contained project, we are executing code we have generated ourselves.
    # A safer approach in a real system would be to use a sandboxed environment.
    exec(indicator_code, {'df': df, 'indicators': indicators})
    
    df['entry_signal'] = eval(entry_code, {'df': df})
    df['exit_signal'] = eval(exit_code, {'df': df})

    # Debug output
    print("\n--- Signal Debug Information ---")
    print(f"Total rows: {len(df)}")
    print(f"Entry signals: {df['entry_signal'].sum()}")
    print(f"Exit signals: {df['exit_signal'].sum()}")
    
    # Show sample of indicators and signals
    indicator_cols = [col for col in df.columns if col.startswith('sma_') or col.startswith('rsi_')]
    if indicator_cols:
        print(f"\nSample indicator values (last 40 rows):")
        print(df[['Date', 'close'] + indicator_cols + ['entry_signal', 'exit_signal']].tail(40).to_string())
    
    # Show where signals occur
    if df['entry_signal'].sum() > 0:
        print(f"\nEntry signal dates:")
        print(df[df['entry_signal']]['Date'].tolist())
    if df['exit_signal'].sum() > 0:
        print(f"\nExit signal dates:")
        print(df[df['exit_signal']]['Date'].tolist())

    # Simulation state
    holding = False
    equity = initial_capital
    entry_price = 0
    trades = []
    equity_curve = []
    peak_equity = initial_capital
    max_drawdown = 0

    print("\n--- Starting Backtest Simulation ---")
    print(f"Initial Capital: ${initial_capital:,.2f}")


    for i, row in df.iterrows():
        # If we get an exit signal and are holding a position, sell at the closing price.
        if row['exit_signal'] and holding:
            exit_price = row['close']
            profit = exit_price - entry_price
            equity += profit
            trades.append({'entry_date': entry_date, 'exit_date': row['Date'], 'entry_price': entry_price, 'exit_price': exit_price, 'profit': profit})
            print(f"{row['Date']}: Sell at {exit_price:.2f}, P/L: ${profit:.2f}, Equity: ${equity:,.2f}")
            holding = False
            entry_price = 0

        # If we get an entry signal and are not holding a position, buy at the closing price.
        if row['entry_signal'] and not holding:
            entry_price = row['close']
            entry_date = row['Date']
            holding = True
            print(f"{row['Date']}: Buy at {entry_price:.2f}")

        # Update equity curve and drawdown
        current_value = equity + (row['close'] - entry_price if holding else 0)
        equity_curve.append(current_value)
        
        if current_value > peak_equity:
            peak_equity = current_value
        
        drawdown = (peak_equity - current_value) / peak_equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # If still holding at the end, close the position
    if holding:
        final_price = df.iloc[-1]['close']
        profit = final_price - entry_price
        equity += profit
        trades.append({'entry_date': entry_date, 'exit_date': df.iloc[-1]['Date'], 'entry_price': entry_price, 'exit_price': final_price, 'profit': profit})
        print(f"--- End of Data: Closing final position at {final_price:.2f} ---")


    # --- Performance Calculation ---
    final_equity = equity
    total_profit = final_equity - initial_capital
    profit_percent = (total_profit / initial_capital) * 100
    num_trades = len(trades)
    wins = [t for t in trades if t['profit'] > 0]
    num_wins = len(wins)
    win_rate = (num_wins / num_trades) * 100 if num_trades > 0 else 0

    results = {
        "initial_capital": initial_capital,
        "final_equity": final_equity,
        "total_profit": total_profit,
        "profit_percent": profit_percent,
        "max_drawdown": max_drawdown,
        "num_trades": num_trades,
        "num_wins": num_wins,
        "win_rate": win_rate,
        "trades": trades,
        "equity_curve": equity_curve
    }
    
    print("\n--- Backtest Finished ---")
    return results

def print_results(results):
    """Prints a formatted summary of the backtest results."""
    print("\n--- Backtest Performance Summary ---")
    print(f"Final Equity:      ${results['final_equity']:,.2f}")
    print(f"Total Profit:      ${results['total_profit']:,.2f} ({results['profit_percent']:.2f}%)")
    print(f"Max Drawdown:      {results['max_drawdown']:.2%}")
    print("-" * 30)
    print(f"Total Trades:      {results['num_trades']}")
    print(f"Winning Trades:    {results['num_wins']}")
    print(f"Win Rate:          {results['win_rate']:.2f}%")
    print("." * 30)
