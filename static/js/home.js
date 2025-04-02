
// 添加主页交互效果
function initHomeInteractions() {
    // 添加卡片悬停效果
    const cards = document.querySelectorAll('.data-card, .glass-card, .nav-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}
