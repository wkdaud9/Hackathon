import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from flask import Blueprint, jsonify
import re
from dotenv import load_dotenv # .env 파일을 읽기 위해 추가

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

bp = Blueprint('scraper', __name__, url_prefix='/scrape')

# --- Supabase 접속 정보 수정 ---
# os.getenv() 함수를 사용해 .env 파일의 값을 읽어옵니다.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# (나머지 코드는 이전과 동일합니다)
# ... get_article_details, get_news_urls, start_scraping 함수들 ...
def get_article_details(url):
    # (이전 코드와 동일)
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        article_id = url.split('/')[-1]
        title_tag = soup.find("h3", class_="tit_view")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
        content_tag = soup.find("div", class_="article_view")
        content = content_tag.get_text() if content_tag else "본문 없음"
        content = re.sub(r'[\s\n\t]+', ' ', content).strip()
        thumbnail_url = "썸네-일 없음"
        meta_tag = soup.find("meta", property="og:image")
        if meta_tag:
            thumbnail_url = meta_tag['content']
        else:
            img_tag = soup.find("img", class_="thumb_g_article")
            if img_tag:
                thumbnail_url = img_tag['src']
        return { 'article_id': article_id, 'title': title, 'content': content, 'thumbnail': thumbnail_url, }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_news_urls(list_url):
    # (이전 코드와 동일)
    response = requests.get(list_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    news_list = []
    article_links = soup.select("a.item_newsheadline2")
    for link in article_links[:10]:
        news_list.append(link['href'])
    return news_list

@bp.route('/start')
def start_scraping():
    """/scrape/start 주소로 접속하면 크롤링을 시작하고 DB에 저장하는 함수"""
    DAUM_NEWS_URL = "https://news.daum.net/"
    print("📰 Daum 뉴스 목록에서 최신 기사 URL 10개를 수집합니다...")
    target_urls = get_news_urls(DAUM_NEWS_URL)
    print(f"✅ URL 수집 완료! 총 {len(target_urls)}개의 기사를 크롤링합니다.\n")
    final_news_data = []
    for url in target_urls:
        details = get_article_details(url)
        if details and details['title'] != "제목 없음":
            final_news_data.append(details)

    if final_news_data:
        print(f"💾 수집된 {len(final_news_data)}개의 뉴스를 Supabase DB에 저장합니다...")
        try:
            supabase.table('articles').upsert(final_news_data).execute()
            print("✅ 데이터 저장(또는 업데이트) 성공!")
            return jsonify({'status': 'success', 'message': f'{len(final_news_data)}개의 뉴스를 저장했습니다.'})
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
    return jsonify({'status': 'no_data', 'message': '저장할 뉴스가 없습니다.'})