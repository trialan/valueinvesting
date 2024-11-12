import pandas as pd
import numpy as np
import matplotlib.dates as mdates


def identify_td_sell_setup(df):
    # Create a copy of the DataFrame to ensure we're not dealing with a view
    df = df.copy()

    # Dictionary to keep track of active setups and their column names
    setup_columns = {}
    current_setup_num = 1

    for i in range(4, len(df) - 4):
        current_date = mdates.num2date(df["Date"][i]).strftime("%Y-%m-%d")

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

            # Start counting from the bar AFTER the flip is complete i+2 <--
            # no??
            for bar in range(i + 1, len(df)):
                bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")

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
                        setup_columns[column_name] = setup_values
                        break
                else:
                    break

    # Add all setup columns to the DataFrame
    for column_name, values in setup_columns.items():
        if 9 in set(values):
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
            for bar in range(i + 1, len(df)):
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
                            #print(f"Reached a buy setup 9 on {bar_date}")
                            setup_reached_9 = True
                            setup_columns[column_name] = setup_values
                            break
                    else:
                        break
                else:
                    break

    # Add all setup columns to the DataFrame
    for column_name, values in setup_columns.items():
        if 9 in set(values):
            df[column_name] = values

    return df


