# src/decision/report.py

import pandas as pd
import os

def generate_market_report():
    path = "data/processed/final_signal.csv"
    if not os.path.exists(path):
        print("❌ 錯誤：找不到數據文件")
        return

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    if df.empty: return

    # 取出最後一筆 (最新真實數據)
    latest = df.iloc[-1]

    c_date = latest["date"].strftime("%Y-%m-%d")
    c_macro = latest["macro_factor"]
    c_ret = latest["final_return"] * 100
    c_sig = latest["signal"]

    print("\n" + "="*60)
    print(f" 【量化模型：市場診斷報告 】")
    print("="*60)
    print(f"數據基準日: {c_date}")
    print(f"1️ 宏觀風險指數 : {c_macro:.2f} " + ("✅ 安全" if c_macro>=1.0 else "🛑 危險"))
    print(f"2 預期年化報酬 : {c_ret:.2f}%")
    print(f"3️ 系統決策訊號 : 【{c_sig}】")

    print("-" * 60)
    print(f" 【最終執行指令】:")

    if c_sig == "BULL":
        print(f"    建議: 2.0x 槓桿 (SSO/期貨)")
    elif c_sig == "NEUTRAL":
        print(f"    建議: 1.0x 現貨 (SPY/VOO)")
    else:
        print(f"    建議: 0.0x 空手 (現金/SHV)")

    print("="*60 + "\n")

if __name__ == "__main__":
    generate_market_report()