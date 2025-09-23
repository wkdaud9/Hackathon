import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from flask import Blueprint, jsonify
import re
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 'scraper'라는 이름의 Blueprint를 생성합니다.
bp = Blueprint('scraper', __name__, url_prefix='/scrape')

# --- Supabase 클라이언트 초기화 ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 크롤링할 카테고리 URL 정의 ---
NEWS_CATEGORIES = {
    'home': 'https://news.daum.net/',
    'economy': 'https://news.daum.net/economic',
    'politics': 'https://news.daum.net/politics',
    'international': 'https://news.daum.net/foreign',
    'it': 'https://news.daum.net/digital'
}

def get_article_details(url, category):
    """기사 상세 페이지에서 HTML과 텍스트 버전의 본문을 모두 추출하는 함수"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        article_id = url.split('/')[-1]

        title_tag = soup.find("h3", class_="tit_view")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

        content_tag = soup.find("div", class_="article_view")
        content_html = str(content_tag) if content_tag else "<p>본문 없음</p>"
        raw_text = content_tag.get_text() if content_tag else "본문 없음"
        content_text = re.sub(r'[\s\n\t]+', ' ', raw_text).strip()

        thumbnail_url = "썸네일 없음"
        meta_tag = soup.find("meta", property="og:image")
        if meta_tag:
            thumbnail_url = meta_tag['content']
        else:
            img_tag = soup.find("img", class_="thumb_g_article")
            if img_tag:
                thumbnail_url = img_tag['src']

        return {
            'article_id': article_id,
            'title': title,
            'content': content_html,
            'content_text': content_text,
            'thumbnail': thumbnail_url,
            'category': category,
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_news_urls(list_url):
    """중복을 제거하여 뉴스 기사 URL을 수집하는 함수"""
    response = requests.get(list_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    
    unique_urls = set()
    link_selectors = ["a.item_newsheadline2", "a.link_txt", "a.link_mainnews"]
    
    article_links = soup.select(', '.join(link_selectors))
    
    for link in article_links:
        href = link.get('href')
        if href and href.startswith('https://v.daum.net/v/'):
            unique_urls.add(href)

    return list(unique_urls)[:10]

@bp.route('/start')
def start_scraping():
    """/scrape/start 주소로 접속하면 모든 카테고리의 뉴스를 크롤링하는 함수"""
    all_scraped_data = []
    
    for category, url in NEWS_CATEGORIES.items():
        print(f"--- 📰 '{category}' 카테고리 크롤링 시작 ---")
        
        target_urls = get_news_urls(url)
        print(f"✅ URL {len(target_urls)}개 수집 완료.")
        
        for article_url in target_urls:
            details = get_article_details(article_url, category)
            if details and details['title'] != "제목 없음":
                all_scraped_data.append(details)

    if all_scraped_data:
        # DB에 저장하기 전, 전체 데이터에서 중복 기사를 최종적으로 제거합니다.
        unique_articles = {article['article_id']: article for article in all_scraped_data}
        final_unique_data = list(unique_articles.values())
        
        print(f"\n💾 수집된 전체 뉴스 {len(all_scraped_data)}개 중, 중복을 제외한 {len(final_unique_data)}개를 Supabase DB에 저장합니다...")
        try:
            # 중복이 제거된 final_unique_data를 DB에 저장
            supabase.table('articles').upsert(final_unique_data).execute()
            print("✅ 데이터 저장(또는 업데이트) 성공!")
            return jsonify({'status': 'success', 'message': f'총 {len(final_unique_data)}개의 뉴스를 저장했습니다.'})
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
    return jsonify({'status': 'no_data', 'message': '저장할 뉴스가 없습니다.'})