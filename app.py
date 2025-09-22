import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# --- Supabase 접속 정보 ---
SUPABASE_URL = "https://vuyiczcaweraqncjxllz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1eWljemNhd2VyYXFuY2p4bGx6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODU0NDg2MiwiZXhwIjoyMDc0MTIwODYyfQ.jUOdJInNFQbGYMU2CCX4dzqu4FpWVV9B_0z0d076IWg"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_article_details(url):
    """(최종) 기사 URL에서 고유 ID를 추출하고 상세 정보를 가져오는 함수"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # ▼▼▼ 고유 ID 추출 로직 추가 ▼▼▼
        # URL("https://v.daum.net/v/20250922213512790")에서 마지막 숫자 부분을 ID로 사용
        article_id = url.split('/')[-1]

        title_tag = soup.find("h3", class_="tit_view")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

        content_tag = soup.find("div", class_="article_view")
        content = content_tag.get_text(strip=True) if content_tag else "본문 없음"

        thumbnail_url = "썸네일 없음"
        meta_tag = soup.find("meta", property="og:image")
        if meta_tag:
            thumbnail_url = meta_tag['content']
        else:
            img_tag = soup.find("img", class_="thumb_g_article")
            if img_tag:
                thumbnail_url = img_tag['src']

        # 반환 데이터에 article_id 추가
        return {
            'article_id': article_id,
            'title': title,
            'content': content,
            'thumbnail': thumbnail_url,
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_news_urls(list_url):
    """목록 페이지에서 뉴스 기사 URL 10개를 수집하는 함수"""
    response = requests.get(list_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    
    news_list = []
    article_links = soup.select("a.item_newsheadline2")
    
    for link in article_links[:10]:
        news_list.append(link['href'])
        
    return news_list

# --- 메인 실행 부분 ---
if __name__ == "__main__":
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
            # 'articles' 테이블에 데이터를 삽입 (upsert 사용)
            # upsert: 데이터가 있으면 업데이트, 없으면 삽입 (중복 방지)
            data, count = supabase.table('articles').upsert(final_news_data).execute()
            print("✅ 데이터 저장(또는 업데이트) 성공!")
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")