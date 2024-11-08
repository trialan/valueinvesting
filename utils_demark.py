import pandas as pd
import time
import logging
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator
import yfinance as yf


def yf_retry_download(symbol, start_date, end_date, max_retries=5, retry_delay=1):
    """ yf.download but it retries up to 5 times if there's an error """
    for attempt in range(max_retries):
        try:
            data = yf.download(symbol, start=start_date, end=end_date)
            if not data.empty:
                return data
            raise Exception("Empty dataset received")
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                logging.error(f"Failed to download {symbol} after {max_retries} attempts: {str(e)}")
                return None
            logging.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
            time.sleep(retry_delay)
    return None


def plot_data(df, title):
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # Plot high-low lines with open-close ticks
    for idx, row in df.iterrows():
        # High-Low line
        ax.plot(
            [row["Date"], row["Date"]],
            [row["Low"], row["High"]],
            color="black",
            linewidth=1,
        )
        # Open tick (left side)
        ax.plot(
            [row["Date"] - 0.2, row["Date"]],
            [row["Open"], row["Open"]],
            color="black",
            linewidth=1,
        )
        # Close tick (right side)
        ax.plot(
            [row["Date"], row["Date"] + 0.2],
            [row["Close"], row["Close"]],
            color="black",
            linewidth=1,
        )
    
    # Format x-axis dates
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    
    # Calculate y-axis scale for relative offsets
    y_range = df["High"].max() - df["Low"].min()
    text_offset = y_range * 0.02  # 2% of total price range for vertical spacing

    # Define distinct colors for countdown columns
    countdown_colors = ['purple', 'blue', 'orange', 'brown', 'darkred']

    # Plot TD Buy Setup numbers for all setup columns
    setup_columns = [col for col in df.columns if col.startswith("TD_Buy_Setup_")]
    for i, column in enumerate(setup_columns):
        vertical_offset = text_offset * (i + 1)  # Multiply by column index for spacing
        for idx, row in df.iterrows():
            if pd.notna(row[column]) and row[column] > 0:
                ax.text(
                    row["Date"],
                    row["High"] + vertical_offset,
                    int(row[column]),
                    color="green",
                    fontsize=12,
                    ha="center",
                )

    # Plot TD Sell Setup numbers for all setup columns
    setup_columns = [col for col in df.columns if col.startswith("TD_Sell_Setup_")]
    for i, column in enumerate(setup_columns):
        vertical_offset = text_offset * (i + 1)  # Multiply by column index for spacing
        for idx, row in df.iterrows():
            if pd.notna(row[column]) and row[column] > 0:
                ax.text(
                    row["Date"],
                    row["High"] + vertical_offset,
                    int(row[column]),
                    color="blue",
                    fontsize=12,
                    ha="center",
                )

    # Plot TD Buy Countdown numbers for all countdown columns
    countdown_columns = [col for col in df.columns if col.startswith("TD_Buy_Countdown_")]
    for i, column in enumerate(countdown_columns):
        vertical_offset = text_offset * (i + 1)  # Multiply by column index for spacing
        color = countdown_colors[i % len(countdown_colors)]  # Cycle through colors if more columns than colors
        for idx, row in df.iterrows():
            if pd.notna(row[column]) and row[column] > 0:
                ax.text(
                    row["Date"],
                    row["Low"] - vertical_offset,
                    int(row[column]),
                    color=color,
                    fontsize=12,
                    ha="center",
                )

    # Set labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def get_ohlc_for_date(df, target_date):
    target_date_num = mdates.date2num(datetime.strptime(target_date, "%Y-%m-%d"))
    mask = df["Date"] == target_date_num
    try:
        row = df[mask].iloc[0]
        return {
            "Open": row["Open"],
            "High": row["High"],
            "Low": row["Low"],
            "Close": row["Close"],
        }
    except IndexError:
        return None


