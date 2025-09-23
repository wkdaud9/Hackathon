from flask import Flask
from views import scraper_views # views 폴더의 scraper_views.py 파일을 가져옴

app = Flask(__name__)

# scraper_views.py 파일에 있는 Blueprint(bp)를 앱에 등록
app.register_blueprint(scraper_views.bp)

@app.route('/')
def index():
    return "<h1>뉴스 크롤러 서버</h1><p>/scrape/start 주소로 이동하여 크롤링을 시작하세요.</p>"

if __name__ == '__main__':
    app.run(debug=True)