import os
from flask import Blueprint, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('news', __name__, url_prefix='/news')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bp.route('/<article_id>')
def news_detail_api(article_id):
    """(수정) 조회수를 직접 가져와 1을 더한 후 저장하는 API"""
    try:
        # 1. 먼저 기사 내용을 가져옵니다.
        response = supabase.table('articles').select('*').eq('article_id', article_id).single().execute()
        
        if response.data:
            article = response.data
            current_views = article.get('views', 0) # 현재 조회수 (없으면 0)
            new_views = current_views + 1

            # 2. 조회수를 1 증가시켜 DB에 업데이트합니다.
            supabase.table('articles').update({'views': new_views}).eq('article_id', article_id).execute()

            # 3. 처음에 가져온 기사 데이터를 JSON으로 반환합니다.
            return jsonify(article)
        else:
            return jsonify({'error': 'Article not found'}), 404

    except Exception as e:
        print(f"API Error in news_views: {e}")
        return jsonify({'error': str(e)}), 500