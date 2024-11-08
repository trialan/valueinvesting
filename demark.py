import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

from utils_demark import plot_data, yf_retry_download


def identify_td_buy_countdown(df):
    # Create a copy of the DataFrame to ensure we're not dealing with a view
    df = df.copy()

    # Dictionary to keep track of active countdowns and their column names
    countdown_columns = {}
    current_countdown_num = 1

    # Get all setup columns
    setup_columns = [col for col in df.columns if col.startswith("TD_Buy_Setup_")]

    for i in range(len(df)):
        current_date = mdates.num2date(df["Date"][i]).strftime("%Y-%m-%d")

        # Check for 9's across all setup columns
        for setup_column in setup_columns:
            if df[setup_column][i] == 9:
                #print(f"\n===== New Setup Found at {current_date} in {setup_column} =====")
                countdown = 0
                previous_countdown_close = None
                start_index = i - 8

                # Verify setup sequence starts with 1
                if start_index >= 0:  # Add boundary check
                    if df[setup_column][start_index] == 1:
                        countdown_started = False
                        countdown_reached_13 = False
                        countdown_values = np.zeros(len(df))

                        for j, bar in enumerate(range(start_index, len(df))):
                            bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")
                            if countdown < 10:
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
                                    previous_countdown_close = df["Close"][bar]

                                    if countdown == 1:
                                        countdown_started = True
                                        column_name = f"TD_Buy_Countdown_{current_countdown_num}"
                                        countdown_columns[column_name] = countdown_values.copy()
                                        current_countdown_num += 1

                            elif countdown >= 10 and countdown < 13:
                                if bar >= 1:
                                    condition5 = df["Close"][bar] < previous_countdown_close
                                    if condition5:
                                        countdown += 1
                                        countdown_values[bar] = countdown
                                        previous_countdown_close = df["Close"][bar]

                            if countdown == 13:
                                countdown_reached_13 = True
                                break

                        # Only add the countdown values if the countdown started AND reached 13
                        if countdown_started and countdown_reached_13:
                            column_name = f"TD_Buy_Countdown_{current_countdown_num - 1}"
                            countdown_columns[column_name] = countdown_values
                        else:
                            current_countdown_num -= 1

    # Add all countdown columns to the DataFrame
    for column_name, values in countdown_columns.items():
        df[column_name] = values

    return df

def identify_td_sell_setup(df):
    # Create a copy of the DataFrame to ensure we're not dealing with a view
    df = df.copy()

    # Dictionary to keep track of active setups and their column names
    setup_columns = {}
    current_setup_num = 1

    for i in range(4, len(df) - 4):
        current_date = mdates.num2date(df["Date"][i]).strftime("%Y-%m-%d")
        
        # Prevent index out of bounds
        if i + 1 >= len(df):
            break

        # Check for Bullish TD Price Flip:
        # First bar's close must be LESS THAN close 4 bars before
        # Second bar's close must be GREATER THAN close 4 bars before
        bullish_price_flip = (
            df["Close"][i] < df["Close"][i - 4]
            and df["Close"][i + 1] > df["Close"][i + 1 - 4]
        )

        if bullish_price_flip:
            count = 0
            setup_started = False
            setup_reached_9 = False
            setup_values = np.zeros(len(df))

            # Start counting from the bar AFTER the flip is complete (i+2)
            for bar in range(i + 2, len(df)):
                bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")

                if bar - 4 >= 0:
                    if df["Close"][bar] > df["Close"][bar - 4]:
                        count += 1
                        setup_values[bar] = count

                        if count == 1:
                            setup_started = True
                            column_name = f"TD_Sell_Setup_{current_setup_num}"
                            setup_columns[column_name] = setup_values.copy()
                            current_setup_num += 1

                        if count == 9:
                            setup_reached_9 = True
                            break
                    else:
                        break
                else:
                    break

            # Only add the setup values if the setup started AND reached 9
            if setup_started and setup_reached_9:
                column_name = f"TD_Sell_Setup_{current_setup_num - 1}"
                setup_columns[column_name] = setup_values
            else:
                current_setup_num -= 1

    # Add all setup columns to the DataFrame
    for column_name, values in setup_columns.items():
        df[column_name] = values

    return df


def identify_td_buy_setup(df):
    # Create a copy of the DataFrame to ensure we're not dealing with a view
    df = df.copy()

    # Dictionary to keep track of active setups and their column names
    setup_columns = {}
    current_setup_num = 1

    for i in range(4, len(df) - 4):
        current_date = mdates.num2date(df["Date"][i]).strftime("%Y-%m-%d")
        
        # Prevent index out of bounds
        if i + 1 >= len(df):
            break

        # Check for Bearish TD Price Flip
        bearish_price_flip = (
            df["Close"][i] > df["Close"][i - 4]
            and df["Close"][i + 1] < df["Close"][i + 1 - 4]
        )

        if bearish_price_flip:
            count = 0
            setup_started = False
            setup_reached_9 = False
            setup_values = np.zeros(len(df))

            # Start counting from the bar AFTER the flip is complete (i+2)
            for bar in range(i + 2, len(df)):
                bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")

                if bar - 4 >= 0:
                    if df["Close"][bar] < df["Close"][bar - 4]:
                        count += 1
                        setup_values[bar] = count

                        if count == 1:
                            setup_started = True
                            column_name = f"TD_Buy_Setup_{current_setup_num}"
                            setup_columns[column_name] = setup_values.copy()
                            current_setup_num += 1

                        if count == 9:
                            setup_reached_9 = True
                            break
                    else:
                        break
                else:
                    break

            # Only add the setup values if the setup started AND reached 9
            if setup_started and setup_reached_9:
                column_name = f"TD_Buy_Setup_{current_setup_num - 1}"
                setup_columns[column_name] = setup_values
            else:
                current_setup_num -= 1

    # Add all setup columns to the DataFrame
    for column_name, values in setup_columns.items():
        df[column_name] = values

    return df


if __name__ == "__main__":
    ticker = "^HSI"
    start_date = "2023-07-01"
    end_date = "2023-09-08"
    data = yf_retry_download(ticker, start_date, end_date)
    data.reset_index(inplace=True)
    data["Date"] = data["Date"].map(mdates.date2num)

    # Initialize indicators
    data["TD_Buy_Setup"] = np.nan
    data["TD_Buy_Countdown"] = np.nan

    # Identify TD Buy Setup and Countdown
    data = identify_td_buy_setup(data)
    data = identify_td_sell_setup(data)
    data = identify_td_buy_countdown(data)

    plot_data(data, f"Combo signals on {ticker} for {start_date}-{end_date}")
