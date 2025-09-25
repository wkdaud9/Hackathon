import os
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request, session
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client



load_dotenv()
bp = Blueprint('llm', __name__, url_prefix='/api')

# Gemini 클라이언트 초기화
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Supabase 클라이언트도 필요하므로 추가
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


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
        
        # 2. Gemini API 호출하여 요약
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"다음 뉴스 기사를 10대 청소년들이 이해할 수 있도록 최대한 쉽게 풀어서 써줘. *이나 이런 특수기호는 꼭 필요할 때만 쓰고, 웬만하면 줄글 형태로 작성해줘. 이 말에 대답하지 말고 바로 내가 부탁한 일을 해.:\n\n{text_content}"
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        ai_response = model.generate_content(prompt, safety_settings=safety_settings)
        summary = ai_response.text
        
        return jsonify({'summary': summary})

    except Exception as e:
        print(f"LLM Summarize API Error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/define', methods=['POST'])
def define_word_in_context():
    data = request.get_json()
    word = data.get('word')
    context = data.get('context')

    if not word or not context:
        return jsonify({'error': '단어와 문맥 정보가 모두 필요합니다.'}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""다음 문장에서 밑줄 친 단어의 뜻을 설명해 줘. 설명은 국립국어원 표준국어대사전의 정의처럼 간결하고 명확한 스타일로, 한 문장으로 해줘. 문장: "{context}" 단어: "{word}" """
        response = model.generate_content(prompt)
        definition = response.text.strip()
        
        # 로그인 상태라면, 검색한 단어로 기록
        if 'user' in session:
            try:
                supabase.table('user_word_history').insert({
                    'user_id': session['user']['id'],
                    'word': word,
                    'definition': definition
                }).execute()
            except Exception as e:
                print(f"Word history logging failed: {e}")

        return jsonify({'word': word, 'definition': definition})

    except Exception as e:
        return jsonify({'error': str(e)}), 500