import streamlit as st
from chains.review_chain import generate_final_essays

def render_step7():
    st.header("7단계: 최종 초안 검토 (Review)")
    st.markdown("---")
    
    state = st.session_state.resume_state
    
    # 6단계 완료 여부 체크
    if "draft_selections" not in state:
        st.error("⚠️ 6단계(초안 선택)가 완료되지 않았습니다.")
        if st.button("👈 6단계로 이동"):
            state["current_step"] = 6
            st.rerun()
        return

    st.info("💡 6단계에서 선택한 초안과 피드백을 바탕으로 최종 자기소개서를 생성합니다.")

    # 최종 초안 생성 버튼 (또는 이미 생성된 경우 표시)
    # if "confirmed_essays" not in state:
#         with st.spinner("피드백을 반영하여 최종안을 다듬고 있습니다..."):
#             try:
#                 final_essays = generate_final_essays(state)
#                 state["confirmed_essays"] = final_essays
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"❌ 생성 중 오류 발생: {e}")
#                 return

    # 테스트용 설정
    if st.button("🚀 최종 초안 생성하기", type="primary", use_container_width=True):
        with st.spinner("피드백을 반영하여 최종안을 다듬고 있습니다..."):
            try:
                final_essays = generate_final_essays(state)
                state["confirmed_essays"] = final_essays
                st.rerun()
            except Exception as e:
                st.error(f"❌ 생성 중 오류 발생: {e}")
                return
    
    # 결과 표시
    if "confirmed_essays" in state:
        final_essays = state["confirmed_essays"]
        questions = state.get("essay_questions", [])
        
        if not final_essays:
            st.warning("⚠️ 생성된 결과가 없습니다. (review_chain 로직 미구현 상태)")
            # 디버깅을 위해 선택된 원본이라도 보여줄 수 있는 로직이 있으면 좋겠지만,
            # 현재는 지시대로 빈 함수이므로 비어있음으로 처리
        
        for i, q in enumerate(questions):
            q_idx = str(i + 1)
            q_text = q.get("question_text", f"문항 {q_idx}")
            
            st.markdown(f"#### 📝 문항 {q_idx}")
            st.write(f"**Q. {q_text}**")
            
            # 생성된 최종본 가져오기
            content = final_essays.get(q_idx, "내용이 생성되지 않았습니다.")
            
            st.text_area(
                f"최종안 - 문항 {q_idx}",
                value=content,
                height=400,
                key=f"final_essay_{i}"
            )
            st.markdown("---")

        # 네비게이션
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("👈 이전 단계"):
                state["current_step"] = 6
                st.rerun()
        
        with col2:
            if st.button("✅ 최종 확정 및 다음 단계로", type="primary", use_container_width=True):
                # 수정된 내용 저장 (사용자가 text_area에서 수정했을 수 있음)
                for i, q in enumerate(questions):
                    q_idx = str(i + 1)
                    # key로 접근하여 현재 text_area의 값을 가져옴
                    edited_content = st.session_state.get(f"final_essay_{i}")
                    if edited_content:
                        state["confirmed_essays"][q_idx] = edited_content
                
                if 7 not in state["completed_steps"]:
                    state["completed_steps"].append(7)
                
                state["current_step"] = 8
                st.rerun()
