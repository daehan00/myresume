import streamlit as st
import os
from dotenv import load_dotenv
import app  # Import the main app logic

# 환경 변수 로드
load_dotenv()

# 페이지 설정 (전역 설정, 로그인 화면과 메인 앱 모두에 적용됨)
st.set_page_config(
    page_title="Resume Assistant",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # 비밀번호가 설정되어 있지 않으면 바로 통과 (개발 편의성)
    access_key = os.getenv("ACCESS_KEY")
    if not access_key:
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == access_key:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.header("🔒 Access Required")
        st.text_input(
            "Access Key를 입력하세요", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.header("🔒 Access Required")
        st.text_input(
            "Access Key를 입력하세요", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ Access Key가 올바르지 않습니다.")
        return False
    else:
        # Password correct.
        return True

if check_password():
    # 인증 성공 시 메인 앱 실행
    app.main()
