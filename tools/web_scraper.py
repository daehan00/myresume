"""웹 스크래핑 도구"""
import requests
from bs4 import BeautifulSoup
from typing import Optional


def scrape_job_posting(url: str, timeout: int = 10) -> Optional[str]:
    """채용 공고 URL에서 텍스트 추출
    
    Args:
        url: 채용 공고 URL
        timeout: 요청 타임아웃 (초)
        
    Returns:
        추출된 텍스트 (실패 시 None)
        
    Raises:
        requests.RequestException: 네트워크 오류
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # script, style 태그 제거
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 텍스트 추출 및 정리
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
        
    except requests.RequestException as e:
        print(f"웹 스크래핑 오류: {e}")
        return None
    except Exception as e:
        print(f"파싱 오류: {e}")
        return None
