import pandas as pd

def load_macro_data():
    m2 = pd.read_csv("data/raw/fred/m2.csv")
    gdp = pd.read_csv("data/raw/fred/gdp.csv")
    y10 = pd.read_csv("data/raw/fred/yield_10y.csv")
    y2 = pd.read_csv("data/raw/fred/yield_2y.csv")

    df = m2.merge(gdp, on="date", how="inner")
    df = df.merge(y10, on="date", how="inner")
    df = df.merge(y2, on="date", how="inner")

    df["m2_yoy"] = df["m2"].pct_change(12)
    df["gdp_yoy"] = df["gdp"].pct_change(4)  # GDP usually quarterly

    df["excess_liquidity"] = df["m2_yoy"] - df["gdp_yoy"]
    df["yield_spread"] = df["yield_10y"] - df["yield_2y"]

    df.to_csv("data/processed/macro.csv", index=False)
    return df

if __name__ == "__main__":
    load_macro_data()
