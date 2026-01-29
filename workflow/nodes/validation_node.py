from models.state import ResumeState
from chains.validation_chain import validate_resume_input

def validate_info(state: ResumeState) -> dict:
    """정보 검증 노드"""
    
    print("--- Validation Node ---")
    
    try:
        validation_result = validate_resume_input(state)
        
        # Pydantic 모델을 dict로 변환하여 상태 업데이트
        status_dict = {
            "company_name": validation_result.company_name.status,
            "job_posting": validation_result.job_posting.status,
        }
        
        return {
            "validation_status": status_dict,
            "additional_questions": validation_result.additional_questions,
            "job_posting": validation_result.cleaned_job_posting,  # 정리된 채용공고로 업데이트
            # 전체 통과 여부는 UI나 Edge에서 판단하겠지만, 편의상 상태에 기록할 수도 있음
            # 여기서는 원본 state 스키마에 맞춰 필요한 정보만 업데이트
        }
        
    except Exception as e:
        print(f"Validation Error: {e}")
        # 에러 발생 시 일단 모두 불명확으로 처리하거나 에러 메시지 저장
        return {
            "additional_questions": [f"시스템 에러가 발생했습니다: {str(e)}"]
        }
