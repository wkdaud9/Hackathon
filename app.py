# app.py

from flask import Flask
from views import scraper_views, main_views, news_views, llm_views 

app = Flask(__name__)

# 모든 Blueprint를 등록합니다.
app.register_blueprint(scraper_views.bp)
app.register_blueprint(main_views.bp)
app.register_blueprint(news_views.bp)
app.register_blueprint(llm_views.bp)

if __name__ == '__main__':
    app.run(debug=True)