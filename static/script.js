document.addEventListener('DOMContentLoaded', () => {
    // 1. 주요 HTML 요소들을 미리 찾아둡니다.
    const newsLayout = document.querySelector('.news-layout');
    const rankingList = document.querySelector('.ranking-list');
    const menuLinks = document.querySelectorAll('.category-link');
    const newsLayoutContainer = document.querySelector('.news-layout-container');
    const seeMoreBtn = document.getElementById('see-more-btn');
    const loaderOverlay = document.getElementById('loader-overlay'); // 로딩 오버레이
    
    // 모달 관련 요소
    const modal = document.querySelector('.news-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalOptions = document.getElementById('modal-options');
    const modalResult = document.getElementById('modal-result');
    const summarizeBtn = document.getElementById('summarize-btn');
    const originalLinkBtn = document.getElementById('original-link-btn');
    const closeModalBtn = document.querySelector('.modal-close-btn');

    // 2. 뉴스 데이터를 받아 화면에 그려주는 함수
    const renderNews = (newsData, rankingData) => {
        newsLayout.innerHTML = ''; 
        rankingList.innerHTML = '';

        if (!newsData || newsData.length === 0) {
            newsLayout.innerHTML = '<p>표시할 뉴스가 없습니다.</p>';
            return;
        }

        const featured = newsData[0];
        const featuredHtml = `
            <article class="news-item featured" data-article-id="${featured.article_id}" data-url="${featured.url}">
                <img src="${featured.thumbnail}" alt="${featured.title}" class="image-placeholder">
                <div class="article-content">
                    <h4>${featured.title}</h4>
                </div>
            </article>`;
        newsLayout.insertAdjacentHTML('beforeend', featuredHtml);

        newsData.slice(1).forEach(news => {
            const newsHtml = `
                <article class="news-item" data-article-id="${news.article_id}" data-url="${news.url}">
                    <img src="${news.thumbnail}" alt="${news.title}" class="image-placeholder small">
                    <div class="article-content">
                        <h5>${news.title}</h5>
                    </div>
                </article>`;
            newsLayout.insertAdjacentHTML('beforeend', newsHtml);
        });
        
        if(rankingData && rankingData.length > 0) {
            rankingData.forEach(news => {
                const rankingHtml = `
                    <article class="ranking-item" data-article-id="${news.article_id}" data-url="${news.url}">
                        <img src="${news.thumbnail}" alt="${news.title}" class="image-placeholder rank">
                        <div class="article-content"><h6>${news.title}</h6></div>
                    </article>`;
                rankingList.insertAdjacentHTML('beforeend', rankingHtml);
            });
        } else {
            rankingList.innerHTML = '<p>랭킹 정보가 없습니다.</p>';
        }

        attachModalEvents();
    };

    // 3. 특정 카테고리의 뉴스를 API로 요청하는 함수
    const fetchAndRenderNews = async (category) => {
        newsLayoutContainer.classList.remove('expanded');
        seeMoreBtn.classList.remove('hidden');

        newsLayout.innerHTML = '<p>뉴스를 불러오는 중...</p>';
        rankingList.innerHTML = '<p>랭킹을 불러오는 중...</p>';
        try {
            const response = await fetch(`/api/articles/${category}`);
            const data = await response.json();
            renderNews(data.news_list, data.ranking_list);
        } catch (error) {
            newsLayout.innerHTML = '<p>뉴스를 불러오는데 실패했습니다.</p>';
            console.error("Error fetching news:", error);
        }
    };

    // 4. 메뉴 링크에 클릭 이벤트 할당
    menuLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const category = e.target.dataset.category;
            
            menuLinks.forEach(l => l.classList.remove('active'));
            e.target.classList.add('active');

            fetchAndRenderNews(category);
        });
    });

    // 5. '더보기' 버튼 클릭 이벤트
    seeMoreBtn.addEventListener('click', () => {
        newsLayoutContainer.classList.add('expanded');
        seeMoreBtn.classList.add('hidden');
    });

    // 6. 모달 관련 이벤트들을 할당하는 함수
    const attachModalEvents = () => {
        document.querySelectorAll('.news-item, .ranking-item').forEach(article => {
            article.style.cursor = 'pointer';
            article.addEventListener('click', () => openChoiceModal(article));
        });
    };
    
    // 7. 뉴스 클릭 시 모달을 "선택지" 상태로 여는 함수
    const openChoiceModal = (articleElement) => {
        const title = articleElement.querySelector('h4, h5, h6').textContent;
        const url = articleElement.dataset.url;

        modalTitle.textContent = title;
        originalLinkBtn.href = url;
        summarizeBtn.dataset.url = url;

        modalOptions.style.display = 'flex';
        modalResult.style.display = 'none';
        modalResult.innerHTML = '';
        
        modal.showModal();
    };

    // 8. 'AI로 풀어보기' 버튼 클릭 이벤트
    summarizeBtn.addEventListener('click', async () => {
        const articleUrl = summarizeBtn.dataset.url;
        if (!articleUrl) return;

        modal.close();
        loaderOverlay.classList.remove('hidden');
        setTimeout(() => loaderOverlay.classList.add('visible'), 10);

        try {
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: articleUrl })
            });
            if (!response.ok) throw new Error('요약 정보를 불러오는 데 실패했습니다.');
            const data = await response.json();
            
            modalOptions.style.display = 'none';
            modalResult.style.display = 'block';
            modalResult.innerHTML = `<p>${data.summary.replace(/\n/g, '<br>')}</p>`;
            modal.showModal();

        } catch (error) {
            modalOptions.style.display = 'none';
            modalResult.style.display = 'block';
            modalResult.innerHTML = `<p>${error.message}</p>`;
            modal.showModal();
        } finally {
            loaderOverlay.classList.remove('visible');
            setTimeout(() => loaderOverlay.classList.add('hidden'), 300);
        }
    });

    // 9. 모달 닫기 이벤트
    closeModalBtn.addEventListener('click', () => modal.close());
    modal.addEventListener('click', (e) => (e.target === modal) && modal.close());

    // 10. 페이지가 처음 로드될 때 'home' 카테고리 뉴스를 자동으로 불러옵니다.
    fetchAndRenderNews('home');
});