import os
from flask import Blueprint, render_template, jsonify # jsonify 추가
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('main', __name__) # url_prefix 제거

# ... (Supabase 클라이언트 초기화는 동일)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@bp.route('/')
def index():
    """메인 HTML 뼈대를 렌더링하는 역할만 담당"""
    return render_template('index.html')

# ▼▼▼ 데이터를 제공하는 API 엔드포인트를 새로 만듭니다 ▼▼▼
@bp.route('/api/articles/<category_name>')
def get_articles_api(category_name):
    """카테고리별 뉴스 데이터를 JSON으로 반환하는 API"""
    try:
        query = supabase.table('articles').select('*')
        
        # 'home' 카테고리는 전체 최신순, 나머지는 카테고리별 최신순
        if category_name != 'home':
            query = query.eq('category', category_name)
            
        news_response = query.order('article_id', desc=True).limit(11).execute()

        # 랭킹 데이터도 동일하게 조회
        rank_query = supabase.table('articles').select('*')
        if category_name != 'home':
            rank_query = rank_query.eq('category', category_name)

        ranking_response = rank_query.order('views', desc=True).limit(10).execute()
        
        return jsonify({
            'news_list': news_response.data,
            'ranking_list': ranking_response.data
        })

    except Exception as e:
        print(f"DB 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500