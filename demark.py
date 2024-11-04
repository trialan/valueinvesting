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

    # Get all setup columns
    setup_columns = [col for col in df.columns if col.startswith("TD_Buy_Setup_")]

    for i in range(len(df)):
        current_date = mdates.num2date(df["Date"][i]).strftime("%Y-%m-%d")
        
        # Check for 9's across all setup columns
        for setup_column in setup_columns:
            if df[setup_column][i] == 9:
                print(f"\n===== New Setup Found at {current_date} in {setup_column} =====")
                countdown = 0
                previous_countdown_close = None
                start_index = i - 8

                # Verify setup sequence starts with 1
                if start_index >= 0:  # Add boundary check
                    if df[setup_column][start_index] == 1:
                        print(f"Valid setup confirmed - starts with 1 at index {start_index}")
                        countdown_started = False
                        countdown_reached_13 = False
                        countdown_values = np.zeros(len(df))

                        for j, bar in enumerate(range(start_index, len(df))):
                            bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")
                            print(f"\nChecking bar at {bar_date} (countdown = {countdown})")
                            
                            if countdown < 10:
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

                                print(f"Conditions for countdown <= 10:")
                                print(f"  1. Close <= Low[bar-2]: {condition1}")
                                print(f"  2. Low <= Low[bar-1]: {condition2}")
                                print(f"  3. Close < prev_countdown_close: {condition3}")
                                print(f"  4. Close < Close[bar-1]: {condition4}")

                                if condition1 and condition2 and condition3 and condition4:
                                    countdown += 1
                                    countdown_values[bar] = countdown
                                    print(f"  >>> Countdown incremented to {countdown}")
                                    previous_countdown_close = df["Close"][bar]

                                    if countdown == 1:
                                        countdown_started = True
                                        column_name = f"TD_Buy_Countdown_{current_countdown_num}"
                                        countdown_columns[column_name] = countdown_values.copy()
                                        print(f"  >>> New countdown series started: {column_name}")
                                        current_countdown_num += 1

                            elif countdown >= 10 and countdown < 13:
                                if bar >= 1:
                                    condition5 = df["Close"][bar] < previous_countdown_close
                                    print(f"Condition for countdown > 10:")
                                    print(f"  5. Close < prev_countdown_close: {condition5}")
                                    
                                    if condition5:
                                        countdown += 1
                                        countdown_values[bar] = countdown
                                        print(f"  >>> Countdown incremented to {countdown}")
                                        previous_countdown_close = df["Close"][bar]

                            if countdown == 13:
                                countdown_reached_13 = True
                                print(f"  >>> Countdown completed at {bar_date}")
                                break

                        # Only add the countdown values if the countdown started AND reached 13
                        if countdown_started and countdown_reached_13:
                            column_name = f"TD_Buy_Countdown_{current_countdown_num - 1}"
                            countdown_columns[column_name] = countdown_values
                            print(f"\nCountdown series {column_name} completed successfully")
                        else:
                            current_countdown_num -= 1
                            print(f"\nCountdown series failed - did not reach 13 (stopped at {countdown})")

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
    
    # Calculate y-axis scale for relative offsets
    y_range = df["High"].max() - df["Low"].min()
    text_offset = y_range * 0.02  # 2% of total price range for vertical spacing

    # Define distinct colors for countdown columns
    countdown_colors = ['blue', 'red', 'orange', 'purple', 'brown', 'darkred']

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
        print(f"Relative offset for {column}: {vertical_offset:.2f} ({(vertical_offset/y_range)*100:.1f}% of price range)")

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
        print(f"Relative offset for {column}: {vertical_offset:.2f} ({(vertical_offset/y_range)*100:.1f}% of price range)")

    # Set labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title(title)
    plt.tight_layout()
    plt.show()



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
            print(f"\n===== New Price Flip Found at {current_date} =====")
            count = 0
            setup_started = False
            setup_reached_9 = False
            setup_values = np.zeros(len(df))

            # Check for 9 consecutive bars
            for bar in range(i + 1, len(df)):
                bar_date = mdates.num2date(df["Date"][bar]).strftime("%Y-%m-%d")
                print(f"\nChecking bar at {bar_date} (setup count = {count})")

                if bar - 4 >= 0:
                    if df["Close"][bar] < df["Close"][bar - 4]:
                        count += 1
                        setup_values[bar] = count
                        print(f"  >>> Setup count incremented to {count}")

                        if count == 1:
                            setup_started = True
                            column_name = f"TD_Buy_Setup_{current_setup_num}"
                            setup_columns[column_name] = setup_values.copy()
                            print(f"  >>> New setup series started: {column_name}")
                            current_setup_num += 1

                        if count == 9:
                            setup_reached_9 = True
                            print(f"  >>> Setup completed at {bar_date}")
                            break
                    else:
                        print(f"  >>> Setup interrupted - Close not less than Close[4] ago")
                        break
                else:
                    print(f"  >>> Not enough data to compare")
                    break

            # Only add the setup values if the setup started AND reached 9
            if setup_started and setup_reached_9:
                column_name = f"TD_Buy_Setup_{current_setup_num - 1}"
                setup_columns[column_name] = setup_values
                print(f"\nSetup series {column_name} completed successfully")
            else:
                current_setup_num -= 1
                print(f"\nSetup series failed - did not reach 9 (stopped at {count})")

    # Add all setup columns to the DataFrame
    for column_name, values in setup_columns.items():
        df[column_name] = values

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
    ticker = "^HSI"
    start_date = "2015-04-15"
    end_date = "2015-09-15"
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
