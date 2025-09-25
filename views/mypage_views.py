import os
from flask import Blueprint, render_template, session, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
bp = Blueprint('mypage', __name__, url_prefix='/mypage')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bp.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user_info = session.get('user')
    user_id = user_info['id']
    
    read_history = []
    word_history = []
    
    try:
        # 최근 읽은 기사 5개 (articles 테이블과 JOIN하여 기사 정보 가져오기)
        h_res = supabase.table('user_read_history').select('*, articles(*)').eq('user_id', user_id).order('read_at', desc=True).limit(5).execute()
        read_history = [item['articles'] for item in h_res.data if item.get('articles')]

        # 최근 검색한 단어 5개
        w_res = supabase.table('user_word_history').select('*').eq('user_id', user_id).order('searched_at', desc=True).limit(5).execute()
        word_history = w_res.data
    except Exception as e:
        print(f"My Page data fetching failed: {e}")

    return render_template('mypage.html', user=user_info, read_history=read_history, word_history=word_history)