import streamlit as st
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

st.set_page_config(
    page_title="Resume Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    st.title("Resume Assistant 📝")
    st.write("지원서 작성 보조 시스템에 오신 것을 환영합니다.")
    
    # TODO: 사이드바 및 페이지 라우팅 로직 구현 필요

if __name__ == "__main__":
    main()
