import yfinance as yf
import pandas as pd
from tabulate import tabulate

def get_sp500_tickers():
    # Get S&P 500 tickers using Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    return df['Symbol'].tolist()

def get_pe_ratios(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            pe_ratio = stock.info['trailingPE']
            company_name = stock.info['longName']
            data.append((ticker, company_name, pe_ratio))
        except KeyError:
            # Skip companies with missing PE ratio data
            pass
    return data

def main():
    print("Fetching S&P 500 tickers...")
    tickers = get_sp500_tickers()
    
    print("Retrieving PE ratios...")
    pe_data = get_pe_ratios(tickers)
    
    # Sort the data by PE ratio (lowest to highest)
    pe_data.sort(key=lambda x: x[2])
    
    # Prepare the table
    headers = ["Ticker", "Company Name", "PE Ratio"]
    table = tabulate(pe_data, headers=headers, floatfmt=".2f")
    
    print("\nS&P 500 Companies Ranked by PE Ratio (Lowest to Highest):")
    print(table)

if __name__ == "__main__":
    main()
