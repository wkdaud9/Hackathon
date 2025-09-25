from flask import Flask
# auth_views를 추가로 import 합니다.
from views import scraper_views, main_views, news_views, llm_views, auth_views

app = Flask(__name__)

# 모든 Blueprint를 등록합니다.
app.register_blueprint(scraper_views.bp)
app.register_blueprint(main_views.bp)
app.register_blueprint(news_views.bp)
app.register_blueprint(llm_views.bp)
app.register_blueprint(auth_views.bp) # ◀ auth_views.bp 등록 코드를 추가합니다.

if __name__ == '__main__':
    app.run(debug=True)