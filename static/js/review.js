/**
 * 审核功能相关的JavaScript代码
 */
document.addEventListener('DOMContentLoaded', function() {
    // 监听审核操作单选按钮变化
    const radioButtons = document.querySelectorAll('input[name="action"]');
    const commentField = document.querySelector('#id_comment');
    
    if (radioButtons.length && commentField) {
        const commentGroup = commentField.closest('.form-group');
        const reviewWarning = document.querySelector('.review-warning');
        
        // 显示或隐藏提示信息
        function updateWarning() {
            const selectedAction = document.querySelector('input[name="action"]:checked');
            if (selectedAction && selectedAction.value === 'reject') {
                if (reviewWarning) {
                    reviewWarning.style.display = 'block';
                }
                if (commentGroup) {
                    commentGroup.classList.add('required-field');
                }
                if (!commentField.hasAttribute('required')) {
                    commentField.setAttribute('required', 'required');
                }
            } else {
                if (reviewWarning) {
                    reviewWarning.style.display = 'none';
                }
                if (commentGroup) {
                    commentGroup.classList.remove('required-field');
                }
                if (commentField.hasAttribute('required')) {
                    commentField.removeAttribute('required');
                }
            }
        }
        
        // 初始检查
        updateWarning();
        
        // 添加事件监听
        radioButtons.forEach(function(radio) {
            radio.addEventListener('change', updateWarning);
        });
        
        // 表单提交前验证
        const form = commentField.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                const selectedAction = document.querySelector('input[name="action"]:checked');
                if (selectedAction && selectedAction.value === 'reject' && !commentField.value.trim()) {
                    e.preventDefault();
                    alert('拒绝操作必须填写审核意见');
                    commentField.focus();
                }
            });
        }
    }
    
    // 添加审核历史查看功能
    const reviewHistoryBtn = document.getElementById('view-review-history');
    if (reviewHistoryBtn) {
        reviewHistoryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const contentId = this.dataset.contentId;
            const contentType = this.dataset.contentType;
            
            // 获取审核历史数据
            fetch(`/api/review-history/${contentType}/${contentId}/`)
                .then(response => response.json())
                .then(data => {
                    // 显示审核历史模态框
                    const modalBody = document.querySelector('#reviewHistoryModal .modal-body');
                    if (modalBody) {
                        if (data.history && data.history.length > 0) {
                            let historyHtml = '<div class="list-group">';
                            data.history.forEach(item => {
                                const actionClass = item.action === 'approve' ? 'success' : 'danger';
                                const actionIcon = item.action === 'approve' ? 'check-circle' : 'times-circle';
                                const contentName = item.content_name || item.temp_content_name || `内容 #${item.content_id}`;
                                historyHtml += `
                                <div class="list-group-item">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h6 class="mb-1">
                                            <span class="badge bg-${actionClass}">
                                                <i class="fas fa-${actionIcon} me-1"></i>
                                                ${item.action === 'approve' ? '通过' : '拒绝'}
                                            </span>
                                            <span class="ms-2">${contentName}</span>
                                        </h6>
                                        <small>${item.review_date}</small>
                                    </div>
                                    <p class="mb-1">审核人: ${item.reviewer}</p>
                                    ${item.comment ? `<p class="text-muted small mb-0">审核意见: ${item.comment}</p>` : ''}
                                </div>`;
                            });
                            historyHtml += '</div>';
                            modalBody.innerHTML = historyHtml;
                        } else {
                            modalBody.innerHTML = '<div class="alert alert-info">暂无审核历史记录</div>';
                        }
                    }
                    
                    // 显示模态框
                    const modal = new bootstrap.Modal(document.getElementById('reviewHistoryModal'));
                    modal.show();
                })
                .catch(error => {
                    console.error('获取审核历史失败:', error);
                    alert('获取审核历史记录失败，请稍后再试');
                });
        });
    }
});

/**
 * 快速审核操作
 * @param {string} contentType - 内容类型
 * @param {number} contentId - 内容ID
 * @param {string} action - 审核操作(approve/reject)
 */
function quickReview(contentType, contentId, action) {
    // 获取CSRF令牌
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    // 如果是拒绝操作，需要获取审核意见
    let comment = '';
    if (action === 'reject') {
        comment = prompt('请输入拒绝原因:');
        if (comment === null) {
            return; // 用户取消了操作
        }
        if (!comment.trim()) {
            alert('拒绝操作必须填写审核意见');
            return;
        }
    }
    
    // 发送审核请求
    fetch(`/orange/api/review/${contentType}/${contentId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            action: action,
            comment: comment
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 审核成功，刷新页面
            alert(data.message);
            location.reload();
        } else {
            // 审核失败，显示错误信息
            alert('审核失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('审核操作失败:', error);
        alert('审核操作失败，请稍后再试');
    });
}
