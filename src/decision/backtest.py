import logging
import os
import time

import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from config.path import PathConfig


def run_backtest(path: str | None = None):
    if not os.path.exists(path):
        logging.error(" 錯誤：找不到數據文件，請先執行 main.py。")
        return

    logging.info(" 正在進行 Phase 4 回測：動態槓桿 (Dynamic Leverage)...")

    # 定義最大回撤計算函數
    def calc_max_drawdown(equity_series):
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        return drawdown.min()

    with tqdm(total=5, desc="全流程回測執行中", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {postfix}]") as pbar:

        # 加載數據
        pbar.set_postfix_str("讀取數據 CSV...")
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.sort_values("date").reset_index(drop=True)
        time.sleep(0.3)
        pbar.update(1)

        # 基礎指標計算
        pbar.set_postfix_str("計算市場回報與信號平移...")
        #  計算大盤回報 (Benchmark Return)
        # 用 Close 價格計算
        df["pct_change"] = df["Close"].pct_change()

        # 定義策略邏輯
        # Shift 1: 用上個月的信號操作這個月
        df["signal_shifted"] = df["signal"].shift(1)

        risk_free_rate_annual = 0.03  # 無風險利率 (持有現金時賺的，年化 3%)
        borrowing_cost_annual = 0.05  # 借貸成本 (開槓桿要付的利息 + 耗損，年化 5%)

        rf_monthly = risk_free_rate_annual / 12
        borrow_cost_monthly = borrowing_cost_annual / 12

        def calculate_strategy_return(row):
            sig = row["signal_shifted"]
            market_ret = row["pct_change"]
            if pd.isna(sig): return 0  # noqa: E701

            #  動態槓桿邏輯
            if sig == "BULL":
                #  兩倍槓桿
                leverage = 2.0
                # 回報 = (市場漲跌 * 2) - (借那一半錢的利息成本)
                # 公式: Leverage * Return - (Leverage - 1) * Cost
                strat_ret = (market_ret * leverage) - ((leverage - 1) * borrow_cost_monthly)
                return strat_ret
            elif sig == "NEUTRAL":
                # 一倍槓桿
                return market_ret
            else:  # BEAR
                # 空手
                # 持有現金賺無風險利息
                return rf_monthly

        time.sleep(0.3)
        pbar.update(1)

        # 策略回測執行
        pbar.set_postfix_str("執行動態槓桿回測...")
        df["strategy_return"] = [calculate_strategy_return(row) for _, row in df.iterrows()]
        pbar.update(1)

        # 績效指標分析
        pbar.set_postfix_str("計算淨值曲線與風險指標...")
        # 計算淨值曲線
        # 假設初始資金 100
        df["benchmark_equity"] = (1 + df["pct_change"]).cumprod() * 100
        df["strategy_equity"] = (1 + df["strategy_return"]).cumprod() * 100

        # 填補第一筆 NaN 為 100
        df.loc[0, "benchmark_equity"] = 100
        df.loc[0, "strategy_equity"] = 100

        #  計算績效指標
        total_ret_bench = (df["benchmark_equity"].iloc[-1] / 100) - 1
        total_ret_strat = (df["strategy_equity"].iloc[-1] / 100) - 1

        # 最大回撤
        mdd_bench = calc_max_drawdown(df["benchmark_equity"])
        mdd_strat = calc_max_drawdown(df["strategy_equity"])

        # 夏普比率
        # 簡單年化處理
        if df["pct_change"].std() == 0:
            sharpe_bench = 0
        else:
            sharpe_bench = (df["pct_change"].mean() / df["pct_change"].std()) * (12**0.5)

        if df["strategy_return"].std() == 0:
            sharpe_strat = 0
        else:
            sharpe_strat = (df["strategy_return"].mean() / df["strategy_return"].std()) * (12**0.5)

        time.sleep(0.3)
        pbar.update(1)

        # 準備圖表與報告
        pbar.set_postfix_str("渲染回測報告...")
        time.sleep(0.3)
        pbar.update(1)

    #  生成回測報告
    print("\n" + "=" * 50)
    print(" 【回測：動態槓桿】")
    print("=" * 50)

    label_w = 22  # 標籤寬度
    data_w = 12  # 數據欄位寬度

    # 表頭
    print(f"{'指標名稱':<{label_w}} | {'Benchmark':^{data_w}} | {'Strategy':^{data_w}}")
    print("-" * (label_w + data_w * 2 + 6))

    # 數據行
    print(f"{'總報酬率 (Total Ret)':<{label_w}} | {total_ret_bench * 100:>{data_w}.2f}% | {total_ret_strat * 100:>{data_w}.2f}%")
    print(f"{'最大回撤 (Max DD)':<{label_w}} | {mdd_bench * 100:>{data_w}.2f}% | {mdd_strat * 100:>{data_w}.2f}%")
    print(f"{'夏普比率 (Sharpe)':<{label_w}} | {sharpe_bench:>{data_w}.2f}  | {sharpe_strat:>{data_w}.2f} ")
    print("-" * 60)
    print("=" * 50 + "\n")

    # 7. 畫圖
    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df["benchmark_equity"], label="S&P 500 (1x)", color="gray", linestyle="--", alpha=0.6)
    plt.plot(df["date"], df["strategy_equity"], label="MVP Dynamic (0x-2x)", color="red", linewidth=2)

    plt.title(" Dynamic Leverage vs S&P 500", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Equity (Log Scale)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale("log")  # 開啟對數座標
    plt.show()


if __name__ == "__main__":
    run_backtest(PathConfig.FINAL_SIGNAL_CSV)