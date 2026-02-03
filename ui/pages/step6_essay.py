import streamlit as st
from chains.writing_chain import generate_drafts

def render_step6():
    st.header("6단계: 초안 작성 및 선택")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    # 5단계 완료 여부 체크 (가이드라인 존재 여부)
    if "writing_guidelines" not in state:
        st.error("⚠️ 작성 가이드(Step 5)가 설정되지 않았습니다.")
        if st.button("👈 5단계로 이동"):
            state["current_step"] = 5
            st.rerun()
        return

    # 테스트용 디버깅 코드
    # state에서 generated_drafts를 제거해서 아래 조건문 안으로 들어가도록
    # if "generated_drafts" in state:
    #     del state["generated_drafts"]


    # 1. 초안 생성 (최초 1회)
    if "generated_drafts" not in state:
        # 사용할 모델 정의 (비교용)
        models_to_use = ["gemini-3-pro-preview", "gpt-4.1"]
        
        with st.spinner("🤖 수집된 모든 정보(경험, 리서치, 전략, 가이드)를 바탕으로 2가지 초안을 작성 중입니다..."):
            try:
                # chains/writing_chain.py의 함수 호출 (모델 리스트 전달)
                drafts = generate_drafts(state, models=models_to_use)
                state["generated_drafts"] = drafts
                state["draft_models"] = models_to_use  # 사용된 모델 정보 저장
                
                # 선택 상태 초기화 (기본값: 옵션 A(0))
                state["draft_selections"] = {k: 0 for k in drafts.keys()}
                # 피드백 상태 초기화
                state["draft_feedbacks"] = {k: "" for k in drafts.keys()}
                
                st.success("✅ 초안 작성이 완료되었습니다! 아래에서 마음에 드는 버전을 선택해주세요.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 초안 생성 중 오류 발생: {e}")
                return

    drafts = state["generated_drafts"]
    models_used = state.get("draft_models", ["Model A", "Model B"])
    questions = state.get("essay_questions", [])
    
    st.info("💡 각 문항별로 AI가 생성한 2가지 버전의 초안입니다. 더 적절한 내용을 선택하고, 수정이 필요한 부분은 피드백을 남겨주세요.")

    # 2. 문항별 초안 비교 및 선택 UI
    with st.form(key="draft_selection_form"):
        for i, q in enumerate(questions):
            q_idx = str(i + 1)
            q_text = q.get("question_text", f"문항 {q_idx}")
            
            # 질문 문항 강조 표시 (텍스트 영역 밖)
            st.markdown(f"#### 📝 문항 {q_idx}")
            st.info(f"**질문:** {q_text}")
            
            current_drafts = drafts.get(q_idx, ["내용 없음", "내용 없음"])
            
            # 2열 비교 레이아웃
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"##### 🅰️ 옵션 A ({models_used[0]})")
                st.code(
                    current_drafts[0],
                    height=350
                )
            
            with col2:
                st.markdown(f"##### 🅱️ 옵션 B ({models_used[1]})")
                st.code(
                    current_drafts[1],
                    height=350
                )
            
            # 선택 및 피드백 영역
            sel_col, feed_col = st.columns([1, 2])
            
            with sel_col:
                st.radio(
                    f"Q{q_idx} 선택",
                    options=[0, 1],
                    format_func=lambda x: f"옵션 A ({models_used[0]})" if x == 0 else f"옵션 B ({models_used[1]})",
                    key=f"sel_{i}", # 임시 키 (form_submit 시 state 업데이트용)
                    index=state["draft_selections"].get(q_idx, 0)
                )
                
            with feed_col:
                st.text_area(
                    "💬 피드백 (수정 요청 사항)",
                    value=state["draft_feedbacks"].get(q_idx, ""),
                    placeholder="선택한 옵션에서 보완하고 싶은 내용이나 수정 요청사항을 적어주세요. (다음 단계에서 반영됩니다)",
                    height=100,
                    key=f"feed_{i}"
                )
            
            st.markdown("---")
        
        # 제출 버튼
        submit_col1, submit_col2 = st.columns([1, 3])
        with submit_col2:
            submitted = st.form_submit_button("✅ 선택 및 피드백 완료 (다음 단계로) 👉", type="primary", use_container_width=True)

    # 3. 폼 제출 처리
    if submitted:
        # 폼 내부의 위젯 값들을 state에 저장
        for i, q in enumerate(questions):
            q_idx = str(i + 1)
            
            # 선택값 저장 (session_state 키 규칙에 따름)
            selected_option = st.session_state.get(f"sel_{i}", 0)
            state["draft_selections"][q_idx] = selected_option
            
            # 피드백 저장
            feedback_text = st.session_state.get(f"feed_{i}", "")
            state["draft_feedbacks"][q_idx] = feedback_text
            # (선택된 텍스트 자체를 별도로 저장해두면 7단계에서 쓰기 편함)
            # 여기서는 selections 인덱스만 저장하고 7단계에서 drafts[idx][selected] 로 접근하도록 함
        
        if 6 not in state["completed_steps"]:
            state["completed_steps"].append(6)
        
        st.success("저장되었습니다. 다음 단계로 이동합니다.")
        state["current_step"] = 7
        st.rerun()

    # 하단 이전 버튼 (폼 밖)
    if st.button("👈 이전 단계"):
        state["current_step"] = 5
        st.rerun()
