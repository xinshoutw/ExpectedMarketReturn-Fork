# src/decision/signal_calc.py

import pandas as pd

def calc_final_signal_pipeline():
    print("   [Decision] Merging Macro and Market data...")

    try:
        macro = pd.read_csv("data/processed/macro_factor.csv")
        market = pd.read_csv("data/processed/market_return.csv")
    except FileNotFoundError:
        print("Error: Missing files. Run Macro and Market steps first.")
        return

    # 確保日期格式一致
    macro["date"] = pd.to_datetime(macro["date"])
    market["date"] = pd.to_datetime(market["date"])

    # 合併
    macro = macro.sort_values("date")
    market = market.sort_values("date")
    df = pd.merge_asof(macro, market, on="date", direction="backward")

    # 填補空值
    df["expected_return"] = df["expected_return"].fillna(0.07)

    # 防呆：如果還沒跑 market 新版，可能沒有 trend_signal 欄位
    if "trend_signal" not in df.columns:
        df["trend_signal"] = True

        # 計算最終回報
    df["final_return"] = df["expected_return"] * df["macro_factor"]

    def get_signal(row):
        # 保險 1: 宏觀風控 (Macro Factor < 1.0 -> 跑)
        if row["macro_factor"] < 1.0:
            return "BEAR"

        # 保險 2: 技術面趨勢風控 (跌破均線 -> 跑)
        # 這是避免 2008 年宏觀騙人的關鍵
        if not row["trend_signal"]:
            return "BEAR"

        # 兩者都安全，才看估值
        if row["final_return"] > 0.06:
            return "BULL"
        elif row["final_return"] > 0:
            return "NEUTRAL"
        else:
            return "BEAR"

    df["signal"] = df.apply(get_signal, axis=1)

    output_path = "data/processed/final_signal.csv"
    df.to_csv(output_path, index=False)
    print(f"   [Decision] Final signal saved to {output_path}")

if __name__ == "__main__":
    calc_final_signal_pipeline()