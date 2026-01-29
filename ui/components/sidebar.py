import streamlit as st

def render_sidebar():
    """사이드바 렌더링"""
    # 1. 진행 단계 표시
    state = st.session_state.resume_state
    current_step = state.get("current_step", 1)
    completed_steps = state.get("completed_steps", [])
    
    st.subheader("진행 단계")
    
    steps = {
        1: "입력 수집",
        2: "필수 정보 검증",
        3: "기업/직무 리서치",
        4: "전략 수립",
        5: "작성 요령 가이드",
        6: "초안 작성",
        7: "종합 검토",
        8: "최종 결과"
    }
    
    # 진행률 계산 (1~8단계)
    progress = (current_step - 1) / 7.0 if current_step < 8 else 1.0
    st.progress(min(progress, 1.0))
    
    for step_num, step_name in steps.items():
        # 버튼 라벨 (아이콘 제거, 심플하게)
        # 상태에 따라 텍스트 앞에 아이콘 붙이기
        prefix = ""
        if step_num in completed_steps:
            prefix = "✅ "
        elif step_num == current_step:
            prefix = "🔵 " # 또는 아이콘 없이 색상으로만 구분
            
        label = f"{prefix}{step_num}. {step_name}"
        
        # 버튼 타입 (현재 단계는 primary)
        btn_type = "primary" if step_num == current_step else "secondary"
        
        # 버튼 활성화 여부
        max_accessible_step = max(completed_steps) + 1 if completed_steps else 1
        is_disabled = step_num > max_accessible_step
        
        # 버튼 클릭 시 해당 단계로 이동
        if st.button(label, key=f"side_step_{step_num}", use_container_width=True, type=btn_type, disabled=is_disabled):
            state["current_step"] = step_num
            st.rerun()
            
    st.markdown("---")
    
    # 2. 메타 정보 또는 도움말
    st.caption(f"지원 회사: {state.get('company_name') or '-'}")
    st.caption(f"지원 직무: {state.get('position_name') or '-'}")
    
    # 3. 개발자용 디버그 (설정 확인)
    from config.settings import settings
    if settings.debug:
        st.markdown("---")
        with st.expander("Debug Info"):
            st.json(state)
