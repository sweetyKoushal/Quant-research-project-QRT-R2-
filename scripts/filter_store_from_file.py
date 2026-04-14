import argparse
import pandas as pd
import os


# -------------------------------
# 1. PARSE ARGUMENTS
# -------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Filter and store OHLCV data from file")

    parser.add_argument("--input_file", type=str, required=True,
                        help="Path or URL to parquet file")

    parser.add_argument("--min_price", type=float, default=0,
                        help="Minimum daily price (Low)")
    parser.add_argument("--max_price", type=float, default=0,
                        help="Maximum daily price (High)")
    parser.add_argument("--min_volume", type=int, default=0,
                        help="Minimum volume filter")

    parser.add_argument("--output", type=str, default="stores/output.parquet",
                        help="Output file path")

    return parser.parse_args()


# -------------------------------
# 2. LOAD DATA
# -------------------------------
def load_data(path):
    print("Loading data from file...")
    data = pd.read_parquet(path)
    return data


# -------------------------------
# 3. FILTER DATA
# -------------------------------
def filter_data(data, min_price, max_price, min_volume):
    data["Date"] = pd.to_datetime(data["Date"])

    if min_price > 0:
        data = data[data["Low"] >= min_price]

    if max_price > 0:
        data = data[data["High"] <= max_price]

    if min_volume > 0:
        data = data[data["Volume"] >= min_volume]

    data = data.dropna()
    data = data.sort_values(["ticker", "Date"])

    return data


# -------------------------------
# 4. STORE DATA
# -------------------------------
def store_data(data, output_path):
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    data.to_parquet(output_path)
    print(f"Saved data to {output_path}")


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    args = parse_args()

    data = load_data(args.input_file)

    data = filter_data(
        data,
        args.min_price,
        args.max_price,
        args.min_volume
    )

    store_data(data, args.output)


if __name__ == "__main__":
    main()
