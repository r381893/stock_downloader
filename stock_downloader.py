import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# 設定 Streamlit 頁面
st.set_page_config(
    page_title="台股歷史資料下載工具",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- 資料下載函式 (最兼容版本) ---
def load_data(ticker, start_date, end_date):
    """從 yfinance 抓取股票或指數資料"""
    try:
        # yfinance 的 end_date 不包含當天，所以加一天確保抓到完整區間。
        end_date_inclusive = end_date + timedelta(days=1)

        # 使用 yfinance.download 抓取資料
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date_inclusive.strftime('%Y-%m-%d')
        )

        if data.empty:
            return pd.DataFrame()

        # 選擇需要的欄位: 日期 (Index) 和 收盤價 (Close)
        df = data[['Close']].copy()

        # 重設索引，將日期從索引變成欄位
        df.reset_index(inplace=True)

        # 重新命名欄位
        df.columns = ['日期', '收盤價']

        # 格式化日期為 YYYY-MM-DD
        df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')

        # 確保收盤價只有兩位小數 (選用)
        df['收盤價'] = df['收盤價'].round(2)

        return df
    except Exception as e:
        st.error(f"連線或抓取失敗，請檢查網路設定。原始錯誤: {e}")
        return pd.DataFrame()


# --- 主應用程式邏輯 ---

st.title("📈 台股歷史資料快速下載工具")
st.markdown("請選擇您想查詢的代號與日期區間，可直接複製表格內容至 Excel。")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("參數設定")

    # 標的選項設定 (***已新增富台指相關代號***)
    ticker_options = {
        "^TWII": "加權指數 (台指期基礎) (^TWII)",  # 台指期對應的指數
        "TW50U.FGI": "富時台灣50指數-美元 (富台指概念) (TW50U.FGI)",  # 富台指對應的指數
        "00631L.TW": "元大台灣50正2 (00631L.TW)",
        "2330.TW": "台積電 (2330.TW)",
        "2317.TW": "鴻海 (2317.TW)",
        "006208.TW": "富邦台50 (006208.TW)",
        "^VIX": "VIX恐慌指數 (^VIX)"
    }

    # 選取代號
    display_options = list(ticker_options.values())
    default_index = 0

    selected_name = st.selectbox(
        "選擇標的 (Ticker)",
        options=display_options,
        index=default_index,
        key='ticker_selection'
    )

    # 根據選取的名稱反查 yfinance 代號
    ticker_yf = next(key for key, value in ticker_options.items() if value == selected_name)
    ticker_name = selected_name

    # 日期範圍
    today = date.today()
    default_start_date = today - timedelta(days=365)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日期", default_start_date, max_value=today, key='start_date_input')
    with col2:
        end_date = st.date_input("結束日期", today, max_value=today, key='end_date_input')

    # 檢查日期有效性
    if start_date > end_date:
        st.error("❌ 錯誤：開始日期不能晚於結束日期。請重新選擇。")
        st.stop()

    st.markdown("---")
    # 強制重新執行按鈕
    fetch_button = st.button("點此重新抓取資料", type="primary")

# --- 顯示結果 ---
st.subheader(f"📊 {ticker_name} ({ticker_yf}) 歷史資料")

# 只有在按鈕被按下或第一次載入時才抓取資料
if fetch_button or 'df_data' not in st.session_state:
    st.session_state.df_data = load_data(ticker_yf, start_date, end_date)

df_data = st.session_state.df_data

if not df_data.empty:
    st.info(
        f"✅ 資料區間：**{start_date.strftime('%Y-%m-%d')}** 至 **{end_date.strftime('%Y-%m-%d')}** (共 **{len(df_data)}** 筆)")

    # 顯示表格，方便複製
    st.dataframe(
        df_data,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    st.markdown("---")
    st.markdown("### 📋 複製到 Excel 說明")
    st.markdown(
        "您可以直接在 **上方的表格** 中點擊、全選 (`Ctrl+A`/`Cmd+A`) 並複製 (`Ctrl+C`/`Cmd+C`)，然後貼上到 Excel。")

else:
    st.warning("⚠️ 查無資料，或您選擇的日期範圍內無交易日。請檢查您的選擇。")

# --- 備註 ---
st.sidebar.markdown("---")
st.sidebar.caption("資料來源：Yahoo! Finance (透過 yfinance 函式庫)")
st.sidebar.caption("請確認您的網路沒有代理伺服器或防火牆阻擋連線。")
