import os
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request
import google.generativeai as genai # OpenAI 대신 Gemini 라이브러리 import
from dotenv import load_dotenv

load_dotenv()
bp = Blueprint('llm', __name__, url_prefix='/api')

# --- Gemini API 클라이언트 초기화 ---
# .env 파일에서 키를 가져와 Gemini를 설정합니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@bp.route('/summarize', methods=['POST'])
def summarize_article():
    """요청받은 URL의 기사를 실시간으로 긁어와 Gemini로 요약하는 API"""
    data = request.get_json()
    article_url = data.get('url')

    if not article_url:
        return jsonify({'error': 'URL이 필요합니다.'}), 400

    try:
        # 1. 실시간으로 기사 본문 텍스트만 스크래핑
        response = requests.get(article_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, "html.parser")
        content_tag = soup.find("div", class_="article_view")
        text_content = content_tag.get_text() if content_tag else ""

        if not text_content:
            return jsonify({'summary': '기사 내용을 불러올 수 없습니다.'})
        
        # 2. Gemini API 호출
        model = genai.GenerativeModel('gemini-2.5-flash') # 사용할 모델 선택
        prompt = f"다음 뉴스 기사를 초등학생도 이해할 수 있도록 세 문단으로 쉽고 명료하게 풀어서 설명해줘:\n\n{text_content}"
        
        response = model.generate_content(prompt)
        summary = response.text
        
        return jsonify({'summary': summary})

    except Exception as e:
        print(f"LLM API Error: {e}")
        return jsonify({'error': str(e)}), 500