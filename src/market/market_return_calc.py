# src/market/market_return_calc.py

import pandas as pd
import yfinance as yf

def calc_market_return_pipeline():
    print("   [Market] Fetching S&P 500 data from yfinance...")

    # 1. 抓取資料
    try:
        sp500 = yf.download("^GSPC", period="max", interval="1mo", progress=False)
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return

    if sp500.empty:
        print("❌ 錯誤: 下載到的資料為空 (Empty DataFrame)")
        return


    # 檢查是否為 MultiIndex
    if isinstance(sp500.columns, pd.MultiIndex):
        try:
            cols = list(sp500)

            if any("Close" in str(c) for c in cols):
                sp500.columns = [c[0] for c in cols]

        except Exception as e:
            print(f"⚠️ 欄位攤平發生錯誤: {e}")

    current_cols = list(sp500)

    if "Close" not in current_cols:
        if "Adj Close" in current_cols:
            sp500.rename(columns={"Adj Close": "Close"}, inplace=True)
        else:
            print(f"❌ 嚴重錯誤: 找不到 Close 欄位。目前的欄位是: {current_cols}")
            return

    sp500 = sp500[["Close"]].copy()

    # --- 以下邏輯不變 ---

    # 處理日期索引
    if not isinstance(sp500.index, pd.DatetimeIndex):
        sp500.index = pd.to_datetime(sp500.index)

    sp500.index = sp500.index.to_series().dt.to_period("M").dt.to_timestamp()
    sp500.index.name = "date"
    sp500.reset_index(inplace=True)

    # 2. 計算均值回歸 (Mean Reversion)
    sp500["ma_24"] = sp500["Close"].rolling(24).mean()
    sp500["bias"] = (sp500["Close"] - sp500["ma_24"]) / sp500["ma_24"]

    # 3. 定義預期回報
    base_return = 0.08
    sensitivity = 0.2
    sp500["expected_return"] = base_return - (sp500["bias"] * sensitivity)

    # 4. 趨勢濾網 (Trend Filter)
    sp500["ma_10"] = sp500["Close"].rolling(10).mean()
    sp500["trend_signal"] = sp500["Close"] > sp500["ma_10"]

    # 5. 存檔
    sp500["date"] = sp500["date"].dt.strftime("%Y-%m-%d")
    sp500["expected_return"] = sp500["expected_return"].fillna(base_return)
    sp500["trend_signal"] = sp500["trend_signal"].fillna(True)

    output_df = sp500[["date", "Close", "expected_return", "trend_signal"]].copy()

    output_path = "data/processed/market_return.csv"
    output_df.to_csv(output_path, index=False)
    print(f"   ✅ [Market] 資料處理成功！已儲存至 {output_path}")

if __name__ == "__main__":
    calc_market_return_pipeline()