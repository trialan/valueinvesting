import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from tqdm import tqdm


class PositionSizer:
    """
    Base class for position sizing. Allows for different sizing strategies.
    """
    def calculate_position_size(self, ticker, data, market_data, portfolio_value):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_trade_history(self, trade):
        pass  # Optional: Override in subclasses if needed


class FixedAmountPositionSizer(PositionSizer):
    """
    Fixed position sizer that allocates a fixed dollar amount per trade.
    """
    def __init__(self, fixed_amount):
        self.fixed_amount = fixed_amount

    def calculate_position_size(self, ticker, data, market_data, portfolio_value):
        """
        Returns the fixed dollar amount and corresponding position size percentage.
        """
        dollar_size = self.fixed_amount
        position_size_pct = dollar_size / portfolio_value
        return dollar_size, position_size_pct


class KellyPositionSizer(PositionSizer):
    """
    Kelly-based position sizer.
    """
    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.historical_trades = []
        self.current_correlation = 0
        self.concentration_limit = 0.25  # Maximum portfolio concentration

    def calculate_position_size(self, ticker, data, market_data, portfolio_value):
        """
        Calculate position size using multiple factors:
        1. Kelly Criterion (from historical trades)
        2. Volatility scaling
        3. Market correlation adjustment
        4. Portfolio concentration limits
        """
        # Calculate base Kelly fraction
        kelly_fraction = calculate_kelly_fraction(pd.DataFrame(self.historical_trades))

        # Calculate volatility scalar
        vol_scalar = calculate_volatility_scalar(data)

        # Estimate market correlation
        correlation = estimate_market_correlation(data, market_data)

        # Adjust kelly fraction based on correlation
        # Reduce size when correlation is high
        correlation_adj = 1 - (correlation**2)

        # Calculate final position size as percentage of portfolio
        base_size = kelly_fraction * correlation_adj * vol_scalar

        # Apply concentration limits
        position_size = min(base_size, self.concentration_limit)

        # Calculate dollar position size
        dollar_size = portfolio_value * position_size

        return dollar_size, position_size

    def update_trade_history(self, trade):
        """Update trade history for Kelly calculations"""
        self.historical_trades.append(trade)
        # Keep only recent history
        if len(self.historical_trades) > 1000:
            self.historical_trades.pop(0)


def calculate_kelly_fraction(historical_trades_df, lookback_window=100):
    """
    Calculate the Kelly fraction based on recent trade history
    """
    # Use recent trades for more relevant statistics
    recent_trades = historical_trades_df.tail(lookback_window)

    if len(recent_trades) < 20:  # Need minimum sample size
        return 0.1  # Default to 10%

    # Calculate win probability
    p = (recent_trades["return"] > 0).mean()

    # Calculate average win/loss ratio
    avg_win = recent_trades[recent_trades["return"] > 0]["return"].mean()
    avg_loss = abs(recent_trades[recent_trades["return"] < 0]["return"].mean())

    if avg_loss == 0:
        return 0.1

    b = avg_win / avg_loss

    # Calculate Kelly fraction
    kelly = (p * (b + 1) - 1) / b

    # Apply constraints and adjustments
    kelly = max(0, kelly)  # No negative bets
    kelly = min(kelly, 0.25)  # Cap at 25%

    # Use half-Kelly for safety
    half_kelly = kelly * 0.5

    return half_kelly


def calculate_volatility_scalar(data, lookback=20):
    """
    Calculate a position scaling factor based on recent volatility
    """
    recent_returns = data["Close"].pct_change().tail(lookback)
    current_vol = recent_returns.std() * np.sqrt(252)  # Annualized vol
    target_vol = 0.20  # Target 20% annualized volatility

    vol_scalar = target_vol / current_vol
    vol_scalar = max(0.5, min(vol_scalar, 2.0))  # Limit scaling between 0.5x and 2x

    return vol_scalar


def estimate_market_correlation(data, market_data, lookback=60):
    """
    Estimate correlation with the market
    """
    if len(data) < lookback or len(market_data) < lookback:
        return 0.5  # Default if not enough data

    stock_returns = data["Close"].pct_change().tail(lookback)
    market_returns = market_data["Close"].pct_change().tail(lookback)

    correlation = stock_returns.corr(market_returns)
    return correlation


