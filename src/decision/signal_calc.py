import logging
import os
import time
import pandas as pd
from tqdm import tqdm
from config.path import PathConfig


def calc_final_signal_pipeline(
    macro_path: str = PathConfig.MACRO_FACTOR_CSV,
    market_path: str = PathConfig.MARKET_RETURN_CSV,
    breadth_path: str = PathConfig.BREADTH_CSV,
    output_path: str = PathConfig.FINAL_SIGNAL_CSV,
):
    global breadth
    logging.info("   [Decision] Merging Macro, Market, and Breadth data...")

    # 使用 tqdm 建立 5 個階段的動態管理
    with tqdm(
        total=5,
        desc="決策管線執行中",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {postfix}]",
    ) as pbar:
        # 數據讀取與檢查
        pbar.set_postfix_str("讀取原始數據檔案...")
        try:
            macro = pd.read_csv(macro_path)
            market = pd.read_csv(market_path)

            if os.path.exists(breadth_path):
                breadth = pd.read_csv(breadth_path)
                breadth["date"] = pd.to_datetime(breadth["date"])
                has_breadth = True
            else:
                logging.warning(
                    " Warning: Breadth data not found. Skipping breadth check."
                )
                has_breadth = False

        except FileNotFoundError:
            logging.error("Error: Missing files. Run Macro and Market steps first.")
            return

        time.sleep(0.3)
        pbar.update(1)

        # 日期格式統一
        pbar.set_postfix_str("統一日期格式中...")
        macro["date"] = pd.to_datetime(macro["date"])
        market["date"] = pd.to_datetime(market["date"])
        time.sleep(0.3)
        pbar.update(1)

        # 數據合併
        pbar.set_postfix_str("進行資料表合併 (asof merge)...")
        macro = macro.sort_values("date")
        market = market.sort_values("date")
        df = pd.merge_asof(macro, market, on="date", direction="backward")

        if has_breadth:
            breadth = breadth.sort_values("date")
            df = pd.merge_asof(
                df, breadth[["date", "breadth_signal"]], on="date", direction="backward"
            )
            df["breadth_signal"] = df["breadth_signal"].fillna("HEALTHY")
        else:
            df["breadth_signal"] = "HEALTHY"

        time.sleep(0.3)
        pbar.update(1)

        # 多重風控訊號計算
        pbar.set_postfix_str("執行宏觀/技術/廣度交叉判斷...")
        df["expected_return"] = df["expected_return"].fillna(0.07)
        if "trend_signal" not in df.columns:
            df["trend_signal"] = True

        df["final_return"] = df["expected_return"] * df["macro_factor"]

        def get_signal(row):
            #  宏觀風控
            if row["macro_factor"] < 0.8:  # 嚴格一點
                return "BEAR"

            #  技術面趨勢風控
            if not row["trend_signal"]:
                return "BEAR"

            # 市場廣度風控
            if row["breadth_signal"] == "FRAGILE":
                return "NEUTRAL"

            if row["breadth_signal"] == "WEAK":
                return "BEAR"

            #  估值決策
            if row["final_return"] > 0.05 and row["macro_factor"] >= 1.0:
                return "BULL"
            elif row["final_return"] > 0:
                return "NEUTRAL"
            else:
                return "BEAR"

        df["signal"] = [get_signal(row) for _, row in df.iterrows()]
        pbar.update(1)

        # 檔案輸出
        pbar.set_postfix_str("儲存最終信號 CSV...")
        df.to_csv(output_path, index=False)
        time.sleep(0.3)
        pbar.update(1)

    logging.info(f"   [Decision] Final signal saved to {output_path}")


if __name__ == "__main__":
    calc_final_signal_pipeline()
