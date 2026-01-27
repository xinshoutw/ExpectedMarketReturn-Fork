import pandas as pd
import os

FRED_BASE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

SERIES = {
    "m2": "M2SL",
    "gdp": "GDP",
    "yield_10y": "DGS10",
    "yield_2y": "DGS2"
}

SAVE_PATH = "data/raw/fred"

def fetch_fred_series(name, series_id):
    url = FRED_BASE_URL + series_id
    print(f"Fetching {name} from {url}")
    df = pd.read_csv(url)

    if df.empty:
        raise ValueError(f"{name} data is empty!")

    df.columns = ["date", name]
    return df

def update_all_fred():
    os.makedirs(SAVE_PATH, exist_ok=True)

    for name, series_id in SERIES.items():
        df = fetch_fred_series(name, series_id)
        file_path = os.path.join(SAVE_PATH, f"{name}.csv")
        df.to_csv(file_path, index=False)
        print(f"Saved {file_path}")

if __name__ == "__main__":
    update_all_fred()
