import streamlit as st
from workflow.nodes.validation_node import validate_info

def render_step2():
    st.header("2단계: 필수 정보 검증")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    # need_validation 플래그가 True인 경우에만 검증 수행 (step1에서 제출 버튼 눌렀을 때)
    # 다른 페이지에서 돌아온 경우에는 need_validation이 False이므로 검증을 수행하지 않음
    if st.session_state.get("need_validation", False):
        # 검증 수행 중 UI 비활성화
        with st.spinner("입력하신 정보를 분석하고 있습니다..."):
            try:
                result = validate_info(state)
                
                # 상태 업데이트
                state.update(result)
                st.session_state.validation_done = True
                st.session_state.need_validation = False  # 검증 완료 표시
                st.rerun()
            except Exception as e:
                st.session_state.need_validation = False  # 오류가 발생해도 플래그 해제
                st.error(f"❌ 검증 중 오류가 발생했습니다: {str(e)}")
                st.warning("이전 단계로 돌아가서 정보를 확인해주세요.")
                if st.button("👈 1단계로 돌아가기", type="primary"):
                    state["current_step"] = 1
                    st.rerun()
                return
    
    # 검증 결과 표시 (검증이 완료된 경우에만)
    if not st.session_state.get("validation_done", False):
        st.info("📌 검증이 아직 수행되지 않았습니다. 1단계에서 제출 버튼을 눌러주세요.")
        if st.button("👈 1단계로 돌아가기"):
            state["current_step"] = 1
            st.rerun()
        return
    
    validation_status = state.get("validation_status", {})
    additional_questions = state.get("additional_questions", [])
    
    # 전체 통과 여부 확인
    all_pass = all(v == "충분" for v in validation_status.values())
    
    st.markdown("---")
    
    if not all_pass:
        st.error("🚨 일부 정보가 부족합니다. 보완이 필요합니다.")
        
        if additional_questions:
            st.subheader("💡 AI의 제안/질문")
            for q in additional_questions:
                st.info(f"• {q}")
        
        st.warning("이전 단계로 돌아가서 정보를 수정해주세요.")
        
        if st.button("👈 1단계로 돌아가기 (수정)", type="primary"):
            state["current_step"] = 1
            # 재진입 시 다시 검증하도록 플래그 초기화
            if "validation_done" in st.session_state:
                del st.session_state.validation_done
            if "need_validation" in st.session_state:
                del st.session_state.need_validation
            st.rerun()
            
    else:
        st.success("✅ 모든 정보가 충분합니다! 다음 단계로 진행할 수 있습니다.")
        
        # 확인용 데이터 요약 (선택 사항)
        with st.expander("검증된 데이터 요약 보기"):
            st.json(validation_status)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("👈 뒤로 (수정)"):
                state["current_step"] = 1
                if "validation_done" in st.session_state:
                    del st.session_state.validation_done
                if "need_validation" in st.session_state:
                    del st.session_state.need_validation
                st.rerun()
        with col2:
            if st.button("기업 리서치 시작하기 (3단계) 👉", type="primary", use_container_width=True):
                state["current_step"] = 3
                
                # 2단계 완료 처리
                if "completed_steps" not in state:
                    state["completed_steps"] = []
                if 2 not in state["completed_steps"]:
                    state["completed_steps"].append(2)
                    
                st.rerun()

def _render_status_card(title, status):
    """상태 카드 렌더링 헬퍼"""
    colors = {
        "충분": "green",
        "부족": "red",
        "불명확": "orange"
    }
    icon = {
        "충분": "✅",
        "부족": "❌",
        "불명확": "❓"
    }
    
    color = colors.get(status, "gray")
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
            <strong>{title}</strong>
            <div style="float: right; color: {color}; font-weight: bold;">
                {icon.get(status, '')} {status}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
