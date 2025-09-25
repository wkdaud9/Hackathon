from flask import Blueprint, render_template, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from gotrue.errors import AuthApiError # Supabase 에러 처리를 위해 추가

load_dotenv()
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Supabase 클라이언트 초기화
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- 페이지 보여주기 함수들 ---
@bp.route('/login/')
def login():
    return render_template('login.html')

@bp.route('/signup/')
def signup():
    return render_template('signup.html')

@bp.route('/level-test/')
def level_test():
    return render_template('level-test.html')


# --- 회원가입 API (수정) ---
@bp.route('/signup', methods=['POST'])
def signup_post():
    """회원가입 폼 데이터를 받아 Supabase에 사용자를 생성하는 API"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        level = data.get('level')

        if not all([email, password, name, level]):
            return jsonify({'error': '모든 필드를 입력해주세요.'}), 400

        # Supabase Auth를 사용하여 사용자 생성
        res = supabase.auth.sign_up({
            "email": email, "password": password,
            "options": {"data": {'full_name': name, 'user_level': level}}
        })
        
        # 성공 시, 바로 성공 응답을 반환
        return jsonify({'success': True, 'message': '회원가입이 완료되었습니다.'}), 200
        
    except AuthApiError as e:
        # Supabase에서 오는 인증 에러 (예: "User already registered")를 직접 처리
        return jsonify({'error': e.message}), 400
    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500


# --- 로그인 API ---
@bp.route('/login', methods=['POST'])
def login_post():
    """로그인 폼 데이터를 받아 Supabase에 인증을 요청하는 API"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': '이메일과 비밀번호를 입력해주세요.'}), 400

        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        return jsonify({'success': True, 'message': '로그인 성공!', 'session': res.session.model_dump() if res.session else None}), 200

    except AuthApiError as e:
        return jsonify({'error': e.message}), 401
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({'error': '알 수 없는 서버 오류가 발생했습니다.'}), 500