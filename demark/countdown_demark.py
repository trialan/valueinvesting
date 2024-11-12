import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

from utils_demark import plot_data, yf_retry_download
from setup_demark import identify_td_sell_setup, identify_td_buy_setup

MAX_TIMEDELTA = 50

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
                countdown = 0
                previous_countdown_close = None
                start_index = i - 8

                # Verify setup sequence starts with 1
                if start_index >= 0:  # Add boundary check
                    if df[setup_column][start_index] == 1:
                        countdown_started = False
                        countdown_reached_13 = False
                        countdown_values = np.zeros(len(df))
                        countdown_start_index = None  # Track when countdown 1 occurs

                        for j, bar in enumerate(range(start_index, len(df))):
                            bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")
                            if countdown < 13:
                                if bar >= 2:
                                    condition1 = df["Close"][bar] <= df["Low"][bar - 2]
                                else:
                                    condition1 = False

                                if bar >= 1:
                                    condition2 = df["Low"][bar] < df["Low"][bar - 1]
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
                                        countdown_start_index = bar  # Record when countdown 1 occurs
                                        column_name = f"TD_Buy_Countdown_{current_countdown_num}"
                                        countdown_columns[column_name] = countdown_values.copy()
                                        current_countdown_num += 1

                            """
                            elif countdown >= 10 and countdown < 13:
                                if bar >= 1:
                                    condition5 = df["Close"][bar] < previous_countdown_close
                                    if condition5:
                                        countdown += 1
                                        countdown_values[bar] = countdown
                                        previous_countdown_close = df["Close"][bar]
                            """

                            if countdown == 13:
                                #print(f"Reached a buy countdown 13 on {bar_date}")
                                countdown_reached_13 = True

                                # Check if the duration between 1 and 13 is less than or equal to 50 days
                                days_between = bar - countdown_start_index
                                if days_between <= MAX_TIMEDELTA:
                                    countdown_columns[column_name] = countdown_values
                                else:
                                    # Remove the countdown if it took too long to complete
                                    if column_name in countdown_columns:
                                        del countdown_columns[column_name]
                                break

    # Add all countdown columns to the DataFrame
    for column_name, values in countdown_columns.items():
        if 13 in set(values):
            df[column_name] = values

    return df


def identify_td_sell_countdown(df):
    df = df.copy()

    countdown_columns = {}
    current_countdown_num = 1

    setup_columns = [col for col in df.columns if col.startswith("TD_Sell_Setup_")]

    for i in range(len(df)):
        current_date = mdates.num2date(df["Date"][i]).strftime("%Y-%m-%d")

        # Check for 9's across all setup columns
        for setup_column in setup_columns:
            if df[setup_column][i] == 9:
                countdown = 0
                previous_countdown_close = None
                start_index = i - 8

                # Verify setup sequence starts with 1
                if start_index >= 0:  # Add boundary check
                    assert df[setup_column][start_index] == 1
                    if df[setup_column][start_index] == 1:
                        countdown_started = False
                        countdown_reached_13 = False
                        countdown_values = np.zeros(len(df))
                        countdown_start_index = None  # Track when countdown 1 occurs

                        for bar in range(start_index, len(df)):
                            bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")
                            # Different conditions for bars 1-10 vs 11-13
                            if countdown < 10:
                                # Version II conditions for bars 1-10
                                if bar >= 2:
                                    condition1 = df["Close"][bar] >= df["High"][bar - 2]
                                else:
                                    condition1 = False

                                if bar >= 1:
                                    condition2 = df["High"][bar] >= df["High"][bar - 1]
                                    condition4 = df["Close"][bar] > df["Close"][bar - 1]
                                else:
                                    condition2 = False
                                    condition4 = False

                                if previous_countdown_close is not None:
                                    condition3 = df["Close"][bar] > previous_countdown_close
                                else:
                                    condition3 = True

                                if countdown == 0:
                                    assert True #condition1 and condition2 and condition3 and condition4

                                if condition1 and condition2 and condition3 and condition4:
                                    countdown += 1
                                    countdown_values[bar] = countdown
                                    previous_countdown_close = df["Close"][bar]
                                    previous_countdown_high = df["High"][bar]

                                    if countdown == 1:
                                        countdown_started = True
                                        countdown_start_index = bar  # Record when countdown 1 occurs
                                        column_name = f"TD_Sell_Countdown_{current_countdown_num}"
                                        countdown_columns[column_name] = countdown_values.copy()
                                        current_countdown_num += 1

                            elif countdown >= 10 and countdown < 13:
                                # Version II conditions for bars 11-13 (less strict)
                                # Only need successive higher closes for bars 11-13
                                condition5_v1 = df["High"][bar] > previous_countdown_high
                                condition5_v2 = df["Close"][bar] > previous_countdown_close
                                #condition5_v3 = df["High"][bar] > 
                                condition5 = condition5_v1 or condition5_v2

                                if condition5:
                                    countdown += 1
                                    countdown_values[bar] = countdown
                                    previous_countdown_close = df["Close"][bar]
                                    previous_countdown_high = df["High"][bar]

                            if countdown == 13:
                                print(f"Reached a sell countdown 13 on {bar_date}")
                                countdown_reached_13 = True
                                
                                # Check if the duration between 1 and 13 is less than or equal to 50 days
                                days_between = bar - countdown_start_index
                                if days_between <= MAX_TIMEDELTA:
                                    countdown_columns[column_name] = countdown_values
                                #else:
                                    #print(f"Discarding countdown sequence - took {days_between} days to complete")

                                    del countdown_columns[column_name]
                                break

    # Add all countdown columns to the DataFrame
    for column_name, values in countdown_columns.items():
        if 13 in set(values):
            df[column_name] = values

    return df


if __name__ == "__main__":
    ticker = "DLTR"
    start_date = "2023-01-01"
    end_date = "2024-11-09"
    data = yf_retry_download(ticker, start_date, end_date)
    data.reset_index(inplace=True)
    data["Date"] = data["Date"].map(mdates.date2num)

    # Identify TD Buy Setup and Countdown
    data = identify_td_buy_setup(data)
    #data = identify_td_sell_setup(data)
    data = identify_td_buy_countdown(data)
    #data = identify_td_sell_countdown(data)
    plot_data(data, f"Combo signals on {ticker} for {start_date}-{end_date}")

