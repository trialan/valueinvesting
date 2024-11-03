import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator
import matplotlib.dates as mdates
from datetime import datetime


def identify_td_buy_countdown(df):
    # Create a copy of the DataFrame to ensure we're not dealing with a view
    df = df.copy()

    # Dictionary to keep track of active countdowns and their column names
    countdown_columns = {}
    current_countdown_num = 1

    for i in range(len(df)):
        if df["TD_Buy_Setup"][i] == 9:
            countdown = 0
            previous_countdown_close = None
            start_index = i - 8

            # Verify setup sequence starts with 1
            if start_index >= 0:  # Add boundary check
                if df["TD_Buy_Setup"][start_index] == 1:
                    countdown_started = False
                    countdown_reached_13 = (
                        False  # New flag to track if countdown reached 13
                    )
                    countdown_values = np.zeros(len(df))

                    for j, bar in enumerate(range(start_index, len(df))):
                        if countdown <= 10:
                            # Apply conditions 1-4
                            if bar >= 2:
                                condition1 = df["Close"][bar] <= df["Low"][bar - 2]
                            else:
                                condition1 = False

                            if bar >= 1:
                                condition2 = df["Low"][bar] <= df["Low"][bar - 1]
                                condition4 = df["Close"][bar] < df["Close"][bar - 1]
                            else:
                                condition2 = False
                                condition4 = False

                            if previous_countdown_close is not None:
                                condition3 = df["Close"][bar] < previous_countdown_close
                            else:
                                condition3 = True

                            if condition1 and condition2 and condition3 and condition4:
                                countdown += 1
                                countdown_values[bar] = countdown
                                current_date = mdates.num2date(
                                    df["Date"][bar]
                                ).strftime("%Y-%m-%d")
                                print(
                                    f" ***** incremented countdown to {countdown} at {current_date}"
                                )
                                previous_countdown_close = df["Close"][bar]

                                # If this is the first increment (countdown == 1), create new column
                                if countdown == 1:
                                    countdown_started = True
                                    column_name = (
                                        f"TD_Buy_Countdown_{current_countdown_num}"
                                    )
                                    countdown_columns[column_name] = (
                                        countdown_values.copy()
                                    )
                                    current_countdown_num += 1

                        elif countdown > 10 and countdown < 13:
                            if bar >= 1:
                                condition5 = df["Close"][bar] < previous_countdown_close
                                if condition5:
                                    countdown += 1
                                    countdown_values[bar] = countdown
                                    current_date = mdates.num2date(
                                        df["Date"][bar]
                                    ).strftime("%Y-%m-%d")
                                    print(
                                        f" ***** incremented countdown to {countdown} at {current_date}"
                                    )
                                    previous_countdown_close = df["Close"][bar]

                        if countdown == 13:
                            countdown_reached_13 = (
                                True  # Set flag when countdown reaches 13
                            )
                            break

                    # Only add the countdown values if the countdown started AND reached 13
                    if countdown_started and countdown_reached_13:
                        column_name = f"TD_Buy_Countdown_{current_countdown_num - 1}"
                        countdown_columns[column_name] = countdown_values
                    else:
                        # If countdown didn't reach 13, decrement the counter since we won't use this number
                        current_countdown_num -= 1

    # Add all countdown columns to the DataFrame
    for column_name, values in countdown_columns.items():
        df[column_name] = values

    return df


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

    # Plot TD Buy Setup numbers
    for idx, row in df.iterrows():
        if pd.notna(row["TD_Buy_Setup"]) and row["TD_Buy_Setup"] > 0:
            ax.text(
                row["Date"],
                row["High"] + 0.5,
                int(row["TD_Buy_Setup"]),
                color="green",
                fontsize=12,
                ha="center",
            )

    # Plot TD Buy Countdown numbers for all countdown columns
    countdown_columns = [
        col for col in df.columns if col.startswith("TD_Buy_Countdown_")
    ]
    vertical_offset = 0.5  # Initial offset

    for column in countdown_columns:
        for idx, row in df.iterrows():
            if pd.notna(row[column]) and row[column] > 0:
                ax.text(
                    row["Date"],
                    row["Low"] - vertical_offset,
                    int(row[column]),
                    color="purple",
                    fontsize=12,
                    ha="center",
                )
        vertical_offset += 15  # Increment offset for next countdown sequence

    # Set labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title(title)

    plt.tight_layout()
    plt.show()


def old_identify_td_buy_countdown(df):
    # Create a copy of the DataFrame to ensure we're not dealing with a view
    df = df.copy()

    # Initialize countdown array
    countdown_values = np.zeros(len(df))

    for i in range(len(df)):
        if df["TD_Buy_Setup"][i] == 9:
            countdown = 0
            previous_countdown_close = None
            start_index = i - 8

            # Verify setup sequence starts with 1
            if start_index >= 0:  # Add boundary check
                assert df["TD_Buy_Setup"][start_index] == 1

                for j, bar in enumerate(range(start_index, len(df))):
                    if countdown <= 10:
                        # Apply conditions 1-4
                        if bar >= 2:
                            condition1 = df["Close"][bar] <= df["Low"][bar - 2]
                        else:
                            condition1 = False

                        if bar >= 1:
                            condition2 = df["Low"][bar] <= df["Low"][bar - 1]
                            condition4 = df["Close"][bar] < df["Close"][bar - 1]
                        else:
                            condition2 = False
                            condition4 = False

                        if previous_countdown_close is not None:
                            condition3 = df["Close"][bar] < previous_countdown_close
                        else:
                            condition3 = True

                        if condition1 and condition2 and condition3 and condition4:
                            countdown += 1
                            countdown_values[bar] = countdown
                            current_date = mdates.num2date(df["Date"][bar]).strftime(
                                "%Y-%m-%d"
                            )
                            print(
                                f" ***** incremented countdown to {countdown} at {current_date}"
                            )
                            previous_countdown_close = df["Close"][bar]

                    elif countdown > 10 and countdown < 13:
                        if bar >= 1:
                            condition5 = df["Close"][bar] < previous_countdown_close
                            if condition5:
                                countdown += 1
                                countdown_values[bar] = countdown
                                current_date = mdates.num2date(
                                    df["Date"][bar]
                                ).strftime("%Y-%m-%d")
                                print(
                                    f" ***** incremented countdown to {countdown} at {current_date}"
                                )
                                previous_countdown_close = df["Close"][bar]

                    if countdown == 13:
                        break

    # Assign the countdown values to the DataFrame column at the end
    df["TD_Buy_Countdown"] = countdown_values

    return df


def identify_td_buy_setup(df):
    for i in range(4, len(df) - 4):
        """
        Buy setup:
        1. Close[i] > Close[i - 4]
        2. Close[i + 1] < Close[i + 1 - 4]
        """
        if i + 1 >= len(df):
            break  # Prevent index out of bounds

        # Bearish TD Price Flip
        bearish_price_flip = (
            df["Close"][i] > df["Close"][i - 4]
            and df["Close"][i + 1] < df["Close"][i + 1 - 4]
        )

        if bearish_price_flip:
            """
            Check for 9 consecutive bars where the close is less than
            the close four bars before, starting from index i + 1.
            """
            count = 0
            for bar in range(i + 1, len(df)):
                if bar - 4 >= 0:
                    if df["Close"][bar] < df["Close"][bar - 4]:
                        count += 1
                        df.loc[bar, "TD_Buy_Setup"] = count
                        if count == 9:
                            break
                    else:
                        break  # Sequence interrupted
                else:
                    break  # Not enough data to compare
    return df


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


if __name__ == "__main__":
    ticker = "^GSPC"
    start_date = "2023-07-15"
    end_date = "2023-11-01"
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    data["Date"] = data["Date"].map(mdates.date2num)

    # Initialize indicators
    data["TD_Buy_Setup"] = np.nan
    data["TD_Buy_Countdown"] = np.nan

    # Identify TD Buy Setup and Countdown
    data = identify_td_buy_setup(data)
    data = identify_td_buy_countdown(data)

    plot_data(data, f"Combo signals on {ticker} for {start_date}-{end_date}")
