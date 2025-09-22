document.addEventListener('DOMContentLoaded', () => {
    // 로그인 버튼 클릭 이벤트
    const loginButton = document.querySelector('.login-btn');
    if (loginButton) {
        loginButton.addEventListener('click', () => {
            alert('로그인 기능 구현이 필요합니다.');
        });
    }

    // 모든 기사(article) 클릭 시 이벤트
    const articles = document.querySelectorAll('article');
    articles.forEach(article => {
        article.style.cursor = 'pointer';
        article.addEventListener('click', () => {
            const titleElement = article.querySelector('h4, h5, h6');
            if (titleElement) {
                const title = titleElement.innerText;
                alert(`'${title}' 기사를 읽습니다.`);
            }
        });
    });
});