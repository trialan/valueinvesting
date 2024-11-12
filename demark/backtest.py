import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from tqdm import tqdm

from utils_demark import yf_retry_download
from tickers import get_sp500_tickers, get_commodity_tickers, get_crypto_tickers
from setup_demark import identify_td_buy_setup, identify_td_sell_setup
from countdown_demark import identify_td_buy_countdown, identify_td_sell_countdown
from sizing import FixedAmountPositionSizer, KellyPositionSizer


HOLDING_PERIOD_DAYS = 10
NUM_RISING_CLOSES = 2
SIGNAL_LOOKBACK_DAYS = NUM_RISING_CLOSES + 1
START_DATE = "2020-01-01"
END_DATE = "2023-01-01"
INITIAL_CAPITAL = 100000


def add_aggregated_countdown_signal(data):
    countdown_cols = [col for col in data.columns if col.startswith("TD_Sell_Setup")]
    if not countdown_cols:
        # print(f"Warning: No TD Buy Countdown columns found in data")
        data["TD_Signal"] = False
        return data
    data["TD_Signal"] = data[countdown_cols].eq(9).any(axis=1)
    return data


def backtest_portfolio(all_data, position_sizer):
    # Diagnostics
    diagnostics = {
        "total_td_signals": 0,
        "signals_with_rising_closes": 0,
        "trades_executed": 0,
        "insufficient_cash": 0,
    }

    # Collect all potential trades
    potential_trades = []

    for ticker, data in all_data.items():
        if ticker == "^GSPC":
            continue

        signal_dates = data.index[data["TD_Signal"] == True]

        diagnostics["total_td_signals"] += len(signal_dates)

        for signal_date in signal_dates:
            signal_idx = data.index.get_loc(signal_date)

            # Check if there are at least 3 days of data after the signal
            if signal_idx + 3 >= len(data):
                continue

            # Get the next 3 closing prices
            closes = data["Close"].iloc[signal_idx + 1 : signal_idx + 4].values

            # Check if the closes are rising consecutively
            is_rising = all(closes[i] > closes[i - 1] for i in range(1, len(closes)))

            if is_rising:
                diagnostics["signals_with_rising_closes"] += 1

                entry_idx = signal_idx + 4  # Day after the 3rd rising close

                # Ensure entry index is within data range
                if entry_idx >= len(data):
                    continue

                entry_date = data.index[entry_idx]
                entry_price = data["Open"].iloc[entry_idx]
                exit_date = entry_date + timedelta(days=HOLDING_PERIOD_DAYS)

                potential_trades.append({
                    "ticker": ticker,
                    "entry_date": entry_date,
                    "entry_price": entry_price,
                    "exit_date": exit_date,
                })

    # Sort potential trades by entry_date
    potential_trades.sort(key=lambda x: x["entry_date"])

    # Simulate the portfolio over time
    portfolio_value = INITIAL_CAPITAL
    cash = INITIAL_CAPITAL
    active_positions = []
    closed_positions = []
    daily_portfolio_values = []
    max_concurrent_positions = 0

    # Build a list of all dates in the data
    all_dates = sorted(
        set(date for data in all_data.values() for date in data.index)
    )

    # Convert all_dates to a set for faster lookup
    all_dates_set = set(all_dates)

    # Index potential_trades
    trade_idx = 0
    total_trades = len(potential_trades)

    print("\nRunning portfolio backtest...")

    for current_date in tqdm(all_dates):
        # First, check for positions that need to be closed
        positions_to_remove = []
        for position in active_positions:
            if current_date >= position["exit_date"]:
                exit_date = current_date
                # Ensure the exit date is within the data range
                if exit_date not in all_data[position["ticker"]].index:
                    # Skip if exit date is not available (e.g., market holiday)
                    continue
                exit_price = all_data[position["ticker"]].loc[exit_date, "Close"]
                position_return = (exit_price - position["entry_price"]) / position["entry_price"]
                cash += position["shares"] * exit_price

                trade_result = {
                    "ticker": position["ticker"],
                    "entry_date": position["entry_date"],
                    "exit_date": exit_date,
                    "entry_price": position["entry_price"],
                    "exit_price": exit_price,
                    "shares": position["shares"],
                    "initial_value": position["shares"] * position["entry_price"],
                    "final_value": position["shares"] * exit_price,
                    "return": position_return,
                }

                closed_positions.append(trade_result)
                position_sizer.update_trade_history(trade_result)
                positions_to_remove.append(position)

        for position in positions_to_remove:
            active_positions.remove(position)

        # Now, check if any trades are to be entered today
        while trade_idx < total_trades and potential_trades[trade_idx]["entry_date"] == current_date:
            trade = potential_trades[trade_idx]
            trade_idx += 1

            # Calculate position size
            dollar_size, position_size_pct = position_sizer.calculate_position_size(
                trade["ticker"],
                all_data[trade["ticker"]].loc[:current_date],
                all_data["^GSPC"].loc[:current_date],
                portfolio_value,
            )

            # Check if we have enough cash
            if dollar_size <= cash:
                shares = dollar_size / trade["entry_price"]

                new_position = {
                    "ticker": trade["ticker"],
                    "entry_date": trade["entry_date"],
                    "exit_date": trade["exit_date"],
                    "entry_price": trade["entry_price"],
                    "shares": shares,
                }

                active_positions.append(new_position)
                cash -= dollar_size
                diagnostics["trades_executed"] += 1
            else:
                diagnostics["insufficient_cash"] += 1

        # Calculate current portfolio value
        current_portfolio_value = cash
        for position in active_positions:
            if current_date not in all_data[position["ticker"]].index:
                # Skip if current date is not available (e.g., market holiday)
                continue
            current_price = all_data[position["ticker"]].loc[current_date, "Close"]
            current_portfolio_value += position["shares"] * current_price

        portfolio_value = current_portfolio_value
        daily_portfolio_values.append(
            {
                "date": current_date,
                "portfolio_value": portfolio_value,
                "n_positions": len(active_positions),
            }
        )

        max_concurrent_positions = max(max_concurrent_positions, len(active_positions))

    # Prepare results
    portfolio_df = pd.DataFrame(daily_portfolio_values)
    trades_df = pd.DataFrame(closed_positions)

    # Print diagnostic results
    print("\nSignal Flow Analysis:")
    print(f"Total TD Signals: {diagnostics['total_td_signals']}")
    print(f"Signals with Rising Closes: {diagnostics['signals_with_rising_closes']}")
    print(f"Trades Executed: {diagnostics['trades_executed']}")
    print(f"Times Insufficient Cash: {diagnostics['insufficient_cash']}")

    print_stats(portfolio_df, trades_df)
    print(f"Max Concurrent Positions: {max_concurrent_positions}")

    return portfolio_df, trades_df, diagnostics

def print_stats(portfolio_df, trades_df):
    # Calculate strategy statistics
    total_trades = len(trades_df)
    if total_trades > 0:
        win_rate = (trades_df["return"] > 0).mean() * 100
        avg_return = trades_df["return"].mean() * 100
        total_return = (
            (portfolio_df["portfolio_value"].iloc[-1] - INITIAL_CAPITAL)
            / INITIAL_CAPITAL
            * 100
        )

        # Calculate Sharpe Ratio
        daily_returns = portfolio_df["portfolio_value"].pct_change()
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()

        # Calculate max drawdown
        rolling_max = portfolio_df["portfolio_value"].expanding().max()
        drawdowns = (portfolio_df["portfolio_value"] - rolling_max) / rolling_max
        max_drawdown = drawdowns.min() * 100

        print("\nStrategy Results:")
        print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
        print(
            f"Final Portfolio Value: ${portfolio_df['portfolio_value'].iloc[-1]:,.2f}"
        )
        print(f"Total Return: {total_return:.2f}%")
        print(f"PnL: {portfolio_df['portfolio_value'].iloc[-1] - INITIAL_CAPITAL}")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Average Trade Return: {avg_return:.2f}%")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Max Drawdown: {max_drawdown:.2f}%")


def check_rising_closes(data, ticker, idx):
    """Check if there are 3 consecutive rising closes."""
    if idx + NUM_RISING_CLOSES >= len(data[ticker]):
        return False
    closes = data[ticker]["Close"].iloc[idx : idx + NUM_RISING_CLOSES].values
    return all(closes[i] > closes[i - 1] for i in range(1, len(closes)))


def prepare_data(tickers):
    """Download and prepare data for all tickers."""
    print("Downloading and preparing data...")
    all_data = {}

    for ticker in tqdm(tickers):
        data = yf_retry_download(ticker, START_DATE, END_DATE)
        if data is None or len(data) < 50:
            continue

        data.reset_index(inplace=True)
        data["Date"] = data["Date"].map(mdates.date2num)

        # Compute TD Combo indicators
        data = identify_td_buy_setup(data)
        data = identify_td_sell_setup(data)
        #data = identify_td_buy_countdown(data)

        data = add_aggregated_countdown_signal(data)

        # Convert date back to datetime
        data["Date"] = pd.to_datetime(mdates.num2date(data["Date"]))
        data.set_index("Date", inplace=True)

        all_data[ticker] = data

    return all_data


class Position:
    def __init__(self, ticker, entry_date, entry_price, shares, position_value):
        self.ticker = ticker
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.initial_value = position_value
        self.exit_date = entry_date + timedelta(days=HOLDING_PERIOD_DAYS)

    def current_value(self, current_price):
        return self.shares * current_price

    def get_return(self, exit_price):
        return (exit_price * self.shares - self.initial_value) / self.initial_value


if __name__ == "__main__":
    tickers = get_sp500_tickers()
    #tickers = get_crypto_tickers()
    tickers.append("^GSPC")
    all_data = prepare_data(tickers)

    position_sizer = FixedAmountPositionSizer(1000.)
    portfolio_df, trades_df, diagnostics = backtest_portfolio(all_data, position_sizer)


