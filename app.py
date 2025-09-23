# app.py

from flask import Flask
# main_views 뿐만 아니라 news_views도 import 해야 합니다.
from views import scraper_views, main_views, news_views 

app = Flask(__name__)

# 모든 Blueprint를 등록합니다.
app.register_blueprint(scraper_views.bp)
app.register_blueprint(main_views.bp)
app.register_blueprint(news_views.bp) # ◀ 이 줄이 누락되었을 가능성이 높습니다.

if __name__ == '__main__':
    app.run(debug=True)