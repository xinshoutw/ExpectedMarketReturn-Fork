# main.py

import pandas as pd
import matplotlib.pyplot as plt
import os

# Import Pipeline
from src.utils import fred_loader, macro_preprocess, future_mock
from src.macro import macro_factor_calc
from src.market import market_return_calc
from src.decision import signal_calc
from src.decision import report
from src.decision import backtest
from datetime import datetime
def run_pipeline():
    # 我們要補齊從真實數據斷點到這個時間點的空白
    target_date_str = datetime.now().strftime("%Y-%m-%d")

    print("==========================================")
    print(f" MVP Quant Pipeline: Scientific Trend Projection")
    print(f" Target Date : {target_date_str}")
    print("==========================================")

    # Step 1: 更新真實數據 (抓到 2025 年某月為止)
    print("\n[Step 1] Fetching Real World Data...")
    fred_loader.update_all_fred()

    # Step 2: 前處理
    print("\n[Step 2] Preprocessing Macro Data...")
    macro_preprocess.load_macro_data()

    # Step 3: 計算歷史數據 (為了算出趨勢斜率)
    print("\n[Step 3] Calculating Historical Macro Factors...")
    macro_factor_calc.calc_macro_factor_pipeline()

    print("\n[Step 4] Calculating Historical Market Returns...")
    market_return_calc.calc_market_return_pipeline()

    #  Step 5: 科學推算填補空白 (不是亂猜，是慣性外推)
    print(f"\n[Step 5] Projecting Trend to {target_date_str}...")
    try:
        future_mock.mock_future_data(target_date_str=target_date_str)
    except AttributeError:
        print("⚠️ 警告：找不到 mock_future_data")

    # Step 6: 最終合併
    print("\n[Step 6] Generating Final Signals...")
    signal_calc.calc_final_signal_pipeline()

    # Step 7: 報告
    print("\n[Step 7] Analyzing Market Status...")
    report.generate_market_report()

    # Step 8: 回測
    print("\n[Step 8] Running Backtest...")
    backtest.run_backtest()

    # Step 9: 畫圖
    print("\n[Step 9] Visualizing Results...")
    visualize()

    print("\n✅ Pipeline Completed Successfully!")

def visualize():
    path = "data/processed/final_signal.csv"
    if not os.path.exists(path):
        print("No signal file found to plot.")
        return

    df = pd.read_csv(path, parse_dates=["date"])

    # 畫圖：近 5 年 (包含真實數據 + 科學推算)
    recent_date = df["date"].max() - pd.DateOffset(years=5)
    df_recent = df[df["date"] >= recent_date]

    if not df_recent.empty:
        plot_chart(df_recent, "Last 5 Years (Trend Projected)")

def plot_chart(df, title):
    fig, ax1 = plt.subplots(figsize=(14, 7))

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Macro Factor', color='tab:blue', fontsize=12)
    ax1.plot(df["date"], df["macro_factor"], color='tab:blue', label='Macro Factor', linewidth=2, marker='o', markersize=4)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_ylim(0, 1.5)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Expected Return', color='tab:orange', fontsize=12)
    ax2.plot(df["date"], df["final_return"], color='tab:orange', label='Final Return', linewidth=2, marker='s', markersize=4)
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    plt.title(title, fontsize=16)
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_pipeline()