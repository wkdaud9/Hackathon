document.addEventListener("DOMContentLoaded", () => {
  const newsLayout = document.querySelector(".news-layout");
  const rankingList = document.querySelector(".ranking-list");
  const menuLinks = document.querySelectorAll(".category-link");
  const modal = document.querySelector(".news-modal");

  // 뉴스 데이터를 받아 HTML로 변환하고 화면에 렌더링하는 함수
  const renderNews = (newsData, rankingData) => {
    // 기존 뉴스 삭제
    newsLayout.innerHTML = "";
    rankingList.innerHTML = "";

    if (!newsData || newsData.length === 0) {
      newsLayout.innerHTML = "<p>표시할 뉴스가 없습니다.</p>";
      return;
    }

    // 대표 뉴스 렌더링
    const featured = newsData[0];
    const featuredHtml = `
            <article class="news-item featured" data-article-id="${
              featured.article_id
            }">
                <img src="${featured.thumbnail}" alt="${
      featured.title
    }" class="image-placeholder">
                <div class="article-content">
                    <h4>${featured.title}</h4>
                    <p>${(featured.content_text || "").substring(0, 100)}...</p>
                </div>
            </article>`;
    newsLayout.insertAdjacentHTML("beforeend", featuredHtml);

    // 나머지 뉴스 목록 렌더링
    newsData.slice(1).forEach((news) => {
      const newsHtml = `
                <article class="news-item" data-article-id="${news.article_id}">
                    <img src="${news.thumbnail}" alt="${
        news.title
      }" class="image-placeholder small">
                    <div class="article-content">
                        <h5>${news.title}</h5>
                        <p>${(news.content_text || "").substring(0, 50)}...</p>
                    </div>
                </article>`;
      newsLayout.insertAdjacentHTML("beforeend", newsHtml);
    });

    // 랭킹 렌더링
    if (rankingData && rankingData.length > 0) {
      rankingData.forEach((news) => {
        const rankingHtml = `
                    <article class="ranking-item" data-article-id="${news.article_id}">
                        <img src="${news.thumbnail}" alt="${news.title}" class="image-placeholder rank">
                        <div class="article-content"><h6>${news.title}</h6></div>
                    </article>`;
        rankingList.insertAdjacentHTML("beforeend", rankingHtml);
      });
    } else {
      rankingList.innerHTML = "<p>랭킹 정보가 없습니다.</p>";
    }

    // 새로 생성된 뉴스 아이템들에 모달 이벤트를 다시 연결
    attachModalEvents();
  };

  // 특정 카테고리의 뉴스를 API로 요청하는 함수
  const fetchAndRenderNews = async (category) => {
    newsLayout.innerHTML = "<p>뉴스를 불러오는 중...</p>";
    rankingList.innerHTML = "";
    try {
      const response = await fetch(`/api/articles/${category}`);
      const data = await response.json();
      renderNews(data.news_list, data.ranking_list);
    } catch (error) {
      newsLayout.innerHTML = "<p>뉴스를 불러오는데 실패했습니다.</p>";
      console.error("Error fetching news:", error);
    }
  };

  // 메뉴 링크에 클릭 이벤트 추가
  menuLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault(); // 링크의 기본 동작(페이지 이동) 방지
      const category = e.target.dataset.category;

      // 활성화된 메뉴 스타일 변경
      menuLinks.forEach((l) => l.classList.remove("active"));
      e.target.classList.add("active");

      fetchAndRenderNews(category);
    });
  });

  // --- 모달 로직 (이벤트 부착을 위해 함수로 분리) ---
  const attachModalEvents = () => {
    const allNewsArticles = document.querySelectorAll(
      ".news-item, .ranking-item"
    );
    allNewsArticles.forEach((article) => {
      article.style.cursor = "pointer";
      // 기존 이벤트 리스너가 있다면 제거하고 새로 추가 (중복 방지)
      article.replaceWith(article.cloneNode(true));
    });
    // 복제된 노드에 다시 이벤트 리스너를 달아줌
    document
      .querySelectorAll(".news-item, .ranking-item")
      .forEach((article) => {
        article.style.cursor = "pointer";
        article.addEventListener("click", async () => {
          // (기존 모달 이벤트 로직과 동일)
          const articleId = article.dataset.articleId;
          if (!articleId) return;
          modal.querySelector("#modal-title").textContent = "로딩 중...";
          modal.querySelector("#modal-content-body").innerHTML = "";
          modal.showModal();
          try {
            const response = await fetch(`/news/${articleId}`);
            const data = await response.json();
            modal.querySelector("#modal-title").textContent = data.title;
            modal.querySelector("#modal-content-body").innerHTML = data.content;
          } catch (error) {
            modal.querySelector("#modal-title").textContent = "오류";
            modal.querySelector("#modal-content-body").textContent =
              "기사를 불러오지 못했습니다.";
          }
        });
      });
  };

  // 모달 닫기 이벤트
  modal
    .querySelector(".modal-close-btn")
    .addEventListener("click", () => modal.close());
  modal.addEventListener("click", (e) => e.target === modal && modal.close());

  // 페이지가 처음 로드될 때 'home' 카테고리 뉴스를 불러옵니다.
  fetchAndRenderNews("home");
});
