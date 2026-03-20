import streamlit as st

# 設定網頁標題
st.set_page_config(page_title="我的 AI 遊戲基地", layout="centered")

st.title("🚀 我的第一個 AI 遊戲")

# 初始化遊戲狀態
if 'count' not in st.session_state:
    st.session_state.count = 0

st.write("這是一個由 AI 協助開發的遊戲專案。")

# 簡單的互動測試
if st.button("點擊測試連線"):
    st.session_state.count += 1
    st.success(f"目前點擊次數：{st.session_state.count}")

st.info("💡 請在終端機輸入 'streamlit run app.py' 來啟動預覽")
