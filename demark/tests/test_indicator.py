import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from utils_demark import yf_retry_download

from setup_demark import identify_td_buy_setup
from countdown_demark import identify_td_buy_countdown

"""
    Backtesting my TD Combo Buy indicator implementation.
"""

start_date = "2023-01-01"
end_date = "2024-11-09"
window = 2

def get_hits_and_misses(ticker, correct_dates):

    try:
        # Get the data
        data = yf_retry_download(ticker, start_date, end_date)
        if data is None or len(data) < 50:
            print(f"Insufficient data for {ticker}")
            return 0, len(correct_dates), 0

        # Prepare data
        data.reset_index(inplace=True)
        data["Date"] = data["Date"].map(mdates.date2num)

        # Calculate indicators
        data = identify_td_buy_setup(data)
        data = identify_td_buy_countdown(data)

        # Convert dates back to datetime for comparison
        data["Date"] = pd.to_datetime(mdates.num2date(data["Date"]))

        # Find all countdown 13 signals
        countdown_cols = [col for col in data.columns if col.startswith("TD_Buy_Countdown_")]
        signal_dates = []

        for col in countdown_cols:
            dates = data[data[col] == 13]["Date"].dt.strftime("%Y-%m-%d").tolist()
            signal_dates.extend(dates)

        signal_dates = sorted(list(set(signal_dates)))  # Remove duplicates

        # Count hits and misses
        hits = 0
        used_signals = set()

        # For each correct date, look for nearby signals
        for correct_date in correct_dates:
            correct_dt = datetime.strptime(correct_date, "%Y-%m-%d")
            found_match = False

            # Look for signals within the window
            for signal_date in signal_dates:
                signal_dt = datetime.strptime(signal_date, "%Y-%m-%d")
                days_diff = abs((signal_dt - correct_dt).days)

                if days_diff <= window and signal_date not in used_signals:
                    hits += 1
                    used_signals.add(signal_date)
                    found_match = True
                    break

            if not found_match:
                print(f"Missed signal for {ticker} on {correct_date}")

        # Calculate all types of errors
        misses = len(correct_dates) - hits  # Signals we should have found but didn't
        false_positives = len(signal_dates) - len(used_signals)  # Extra signals we generated

        if false_positives > 0:
            print(f"Warning: {false_positives} extra signals generated for {ticker}")
            print("Extra signals on:", [d for d in signal_dates if d not in used_signals])

        return hits, misses, false_positives

    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return 0, len(correct_dates), 0


def test_buy_indicators(test_cases):
    """
    Test TD buy signals against known correct dates.
    
    Args:
        test_cases (dict): Dictionary of ticker: [dates] pairs
    """
    total_hits = 0
    total_misses = 0
    total_false_positives = 0
    results = {}

    print("Testing TD Buy Signals...")
    print("-" * 50)

    for ticker, correct_dates in test_cases.items():
        print(f"\nProcessing {ticker}...")
        hits, misses, false_positives = get_hits_and_misses(ticker, correct_dates)

        # Calculate accuracy including false positives as errors
        total_attempts = hits + misses + false_positives
        accuracy = hits / total_attempts if total_attempts > 0 else 0

        results[ticker] = {
            "hits": hits,
            "misses": misses,
            "false_positives": false_positives,
            "accuracy": accuracy
        }

        total_hits += hits
        total_misses += misses
        total_false_positives += false_positives

        print(f"Results for {ticker}:")
        print(f"Hits: {hits}")
        print(f"Misses: {misses}")
        print(f"False Positives: {false_positives}")
        print(f"Accuracy: {accuracy:.2%}")

    # Calculate overall accuracy including false positives
    total_attempts = total_hits + total_misses + total_false_positives
    total_accuracy = total_hits / total_attempts if total_attempts > 0 else 0

    print("\nOverall Results:")
    print("-" * 50)
    print(f"Total Hits: {total_hits}")
    print(f"Total Misses: {total_misses}")
    print(f"Total False Positives: {total_false_positives}")
    print(f"Overall Accuracy: {total_accuracy:.2%}")

    return results


if __name__ == "__main__":
    test_cases = {
        "MMM": ["2023-10-04",
                "2023-10-20",
                "2023-09-21",
                "2023-03-10"],
        "ABT": ["2024-05-29",
                "2023-09-25"],
        "^HSI": ["2023-03-20",
                 "2023-10-20",
                 "2024-07-24"],
        "^MXX": ["2023-10-13",
                 "2023-10-19"],
        "ABNB": ["2023-10-27"],
        "AEE": ["2023-09-27"],
        "ADM": ["2023-03-10",
                "2024-01-18"],
        "BA": ["2024-03-18", #boeing
               "2024-03-13",
               "2023-09-25"],
        "CPT": ["2023-03-23",
                "2023-09-21",
                "2023-10-30"],
        "CVX": ["2024-09-04"], #chevron
        "CINF": ["2023-03-16",
                 "2023-05-30"],
        "CAG": ["2023-02-16",
                "2023-07-31",
                "2023-08-08",
                "2023-08-21",
                "2023-09-01",
                "2023-10-04"],
        "CSX": ["2024-04-24",
                "2024-06-10"],
        "DECK": ["2024-07-25"],
        "DXCM": ["2023-09-18",
                 "2023-09-21"],
        "DLTR": ["2024-11-06",
                 "2024-08-02",
                 "2024-05-22",
                 "2023-09-05"]
        }

    results = test_buy_indicators(test_cases)


