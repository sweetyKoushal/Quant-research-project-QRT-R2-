import argparse
import yfinance as yf
import pandas as pd
import os

# -------------------------------
# 1. PARSE ARGUMENTS
# -------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Fetch, filter, and store OHLCV data")

    parser.add_argument("--tickers", type=str, required=True,
                        help="Comma-separated tickers (e.g. AAPL,MSFT)")
    parser.add_argument("--start", type=str, default="2015-01-01")
    parser.add_argument("--end", type=str, default=None)

    # filters
    parser.add_argument("--min_price", type=float, default=0,
                        help="Minimum daily price (Low)")
    parser.add_argument("--max_price", type=float, default=0,
                        help="Maximum daily price (High)")
    parser.add_argument("--min_volume", type=int, default=0)

    parser.add_argument("--output", type=str, default="stores/data.parquet")

    return parser.parse_args()


# -------------------------------
# 2. CALL API
# -------------------------------
def fetch_ohlcv_data(tickers, start, end):
    all_data = []

    for ticker in tickers:
        try:
            print(f"Fetching {ticker}...")

            df = yf.download(ticker, start=start, end=end, progress=False)

            if df.empty:
                continue

            df = df.reset_index()
            df["ticker"] = ticker

            df = df[["Date", "ticker", "Open", "High", "Low", "Close", "Volume"]]

            all_data.append(df)

        except Exception as e:
            print(f"Error with {ticker}: {e}")

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)


# -------------------------------
# 3. FILTER DATA
# -------------------------------
def filter_data(data, start, end, min_price, max_price, min_volume):
    data["Date"] = pd.to_datetime(data["Date"])

    if start:
        data = data[data["Date"] >= start]

    if end:
        data = data[data["Date"] <= end]

    # MIN price filter (Low)
    if min_price > 0:
        data = data[data["Low"] >= min_price]

    # MAX price filter (High)
    if max_price > 0:
        data = data[data["High"] <= max_price]

    # volume filter
    if min_volume > 0:
        data = data[data["Volume"] >= min_volume]

    data = data.dropna()
    data = data.sort_values(["ticker", "Date"])

    return data


# -------------------------------
# 4. STORE DATA
# -------------------------------
def store_data(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data.to_parquet(output_path)
    print(f"Saved data to {output_path}")


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    args = parse_args()

    tickers = args.tickers.split(",")

    # CALL API
    data = fetch_ohlcv_data(tickers, args.start, args.end)

    if data.empty:
        print("No data fetched.")
        return

    # FILTER DATA
    data = filter_data(
        data,
        args.start,
        args.end,
        args.min_price,
        args.max_price,
        args.min_volume
    )

    # STORE DATA
    store_data(data, args.output)


if __name__ == "__main__":
    main()
