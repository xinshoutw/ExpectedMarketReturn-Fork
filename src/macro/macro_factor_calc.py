# src/macro/macro_factor_calc.py

import pandas as pd

def calc_macro_factor_logic(excess_liquidity, is_inverted):
    """
    純邏輯計算，與資料源解耦
    """
    if is_inverted or excess_liquidity < 0:
        return 0.3
    elif excess_liquidity > 0.02: # 2%
        return 1.0
    else:
        return 0.7

def calc_macro_factor_pipeline():
    """
    Pipeline 入口：讀取資料 -> 呼叫小模組 -> 存檔
    """
    print("   [Macro] Loading processed data...")
    # 讀取 Step 2 產生的 macro.csv
    df = pd.read_csv("data/processed/macro.csv")

    # 1. 呼叫 liquidity 邏輯 (如果你的 liquidity.py 有特殊函式，可以在這用)
    # 這裡示範直接用欄位，因為我們在前處理算好了。
    # 如果未來你想用 liquidity.py 的函式：
    # df["excess_liquidity"] = df.apply(lambda row: liquidity.calc_excess(row["m2"], row["gdp"]), axis=1)

    # 2. 呼叫 yield_curve 邏輯
    # 假設 src/macro/yield_curve.py 有一個 check_inversion(y10, y2)
    # df["inverted"] = df.apply(lambda row: yield_curve.check_inversion(row["yield_10y"], row["yield_2y"]), axis=1)

    # MVP 簡單版直接做：
    df["inverted"] = df["yield_spread"] < 0

    # 3. 計算 Macro Factor
    print("   [Macro] Calculating factors...")
    df["macro_factor"] = df.apply(
        lambda x: calc_macro_factor_logic(x["excess_liquidity"], x["inverted"]),
        axis=1
    )

    # 存檔
    output_path = "data/processed/macro_factor.csv"
    df.to_csv(output_path, index=False)
    print(f"   [Macro] Saved to {output_path}")

if __name__ == "__main__":
    calc_macro_factor_pipeline()