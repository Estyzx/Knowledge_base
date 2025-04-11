document.addEventListener('DOMContentLoaded', function() {
    // 获取认证状态
    const isAuthenticated = document.documentElement.getAttribute('data-authenticated') === 'true';

    // 投票功能
    const voteButton = document.querySelector('.vote-button');
    if (voteButton) {
        voteButton.addEventListener('click', async function() {
            if (!isAuthenticated) {
                window.location.href = '/user/login/';
                return;
            }
            try {
                const questionId = window.location.pathname.split('/').filter(Boolean).pop();
                const response = await fetch(`/expert_qa/vote/question/${questionId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    this.classList.toggle('voted');
                    const voteCount = this.querySelector('span');
                    voteCount.textContent = data.votes_count;
                }
            } catch (error) {
                console.error('Error voting:', error);
            }
        });
    }

    // 分享功能
    const shareButton = document.querySelector('.share-button');
    if (shareButton) {
        shareButton.addEventListener('click', function() {
            if (navigator.share) {
                navigator.share({
                    title: document.querySelector('.question-title').textContent,
                    url: window.location.href
                });
            } else {
                // 复制链接到剪贴板
                navigator.clipboard.writeText(window.location.href)
                    .then(() => alert('链接已复制到剪贴板'));
            }
        });
    }

    // 回答投票功能
    document.querySelectorAll('.answer-action .fa-thumbs-up').forEach(button => {
        button.parentElement.addEventListener('click', async function() {
            if (!isAuthenticated) {
                window.location.href = '/user/login/';
                return;
            }
            const answerId = this.closest('.answer-card').dataset.answerId;
            try {
                const response = await fetch(`/expert_qa/vote/answer/${answerId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    const voteCount = this.querySelector('span');
                    voteCount.textContent = data.votes_count;
                    this.classList.toggle('voted');
                }
            } catch (error) {
                console.error('Error voting for answer:', error);
            }
        });
    });

    // 排序功能
    const sortOptions = document.querySelectorAll('.sort-option');
    sortOptions.forEach(option => {
        option.addEventListener('click', async function() {
            sortOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            const sortType = this.textContent === '按时间' ? 'time' : 
                           this.textContent === '按投票数' ? 'votes' : 'default';
            try {
                const questionId = window.location.pathname.split('/').filter(Boolean).pop();
                const response = await fetch(`/expert_qa/question/${questionId}/answers/?sort=${sortType}`);
                const data = await response.json();
                updateAnswers(data.answers);
            } catch (error) {
                console.error('Error sorting answers:', error);
            }
        });
    });

    // 评论功能
    document.querySelectorAll('.answer-action .fa-comment').forEach(button => {
        button.parentElement.addEventListener('click', function() {
            if (!isAuthenticated) {
                window.location.href = '/user/login/';
                return;
            }
            const answerId = this.closest('.answer-card').dataset.answerId;
            // TODO: 实现评论功能
            alert('评论功能即将上线');
        });
    });

    // 处理采纳答案
    document.querySelectorAll('.accept-answer').forEach(button => {
        button.addEventListener('click', function() {
            if (!isAuthenticated) {
                alert('请先登录');
                return;
            }

            const answerId = this.dataset.answerId;
            fetch(`/expert_qa/accept_answer/${answerId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message || '操作失败');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('操作失败，请稍后重试');
            });
        });
    });

    // 获取CSRF Token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // 处理回答表单提交
    const answerForm = document.getElementById('answer-form');
    if (answerForm) {
        answerForm.addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submit-answer');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>提交中...';
        });
    }

    // 辅助函数
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateAnswers(answers) {
        const answersContainer = document.querySelector('.answers-section');
        // 清空现有回答
        const answersHeader = answersContainer.querySelector('.answers-header');
        answersContainer.innerHTML = '';
        answersContainer.appendChild(answersHeader);

        // 添加新的回答
        answers.forEach(answer => {
            const answerCard = createAnswerCard(answer);
            answersContainer.appendChild(answerCard);
        });
    }

    function createAnswerCard(answer) {
        const template = `
            <div class="answer-card" data-answer-id="${answer.id}">
                <div class="answer-author">
                    <img src="${answer.author.avatar || '/static/default_avatar.png'}" 
                         alt="${answer.author.username}" class="author-avatar">
                    <div class="author-info">
                        <span class="author-name">${answer.author.username}</span>
                        <span class="author-title">${answer.author.expert_profile?.title || ''}</span>
                    </div>
                </div>
                <div class="answer-content">${answer.content}</div>
                <div class="answer-actions">
                    <div class="answer-action ${answer.user_voted ? 'voted' : ''}">
                        <i class="fas fa-thumbs-up"></i>
                        <span>${answer.votes_count}</span>
                    </div>
                    <div class="answer-action">
                        <i class="fas fa-comment"></i>
                        <span>评论</span>
                    </div>
                    <div class="answer-action">
                        <i class="fas fa-share"></i>
                        <span>分享</span>
                    </div>
                </div>
            </div>
        `;
        const div = document.createElement('div');
        div.innerHTML = template.trim();
        return div.firstChild;
    }
});