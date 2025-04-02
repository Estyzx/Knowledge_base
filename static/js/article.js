document.addEventListener('DOMContentLoaded', function () {
    // 初始化错误处理函数 - 优化错误处理和用户反馈
    function handleError(error, message, options = {}) {
        console.error(message, error);
        const defaultOptions = {
            icon: 'error',
            title: '操作失败',
            text: message,
            confirmButtonText: '确定',
            timer: options.autoClose ? 3000 : undefined,
            timerProgressBar: options.autoClose ? true : false
        };
        Swal.fire({...defaultOptions, ...options});
    }

    // 安全地查询DOM元素 - 优化DOM查询操作
    function safeQuerySelector(selector, context = document) {
        try {
            return context.querySelector(selector);
        } catch (error) {
            handleError(error, `查询元素失败: ${selector}`, {autoClose: true});
            return null;
        }
    }
    
    // 获取CSRF令牌的通用函数 - 减少代码重复
    function getCsrfToken() {
        try {
            const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
            return csrfElement ? csrfElement.value : '';
        } catch (error) {
            console.warn('获取CSRF令牌失败:', error);
            return '';
        }
    }

    // 评论表单异步提交
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const textarea = this.querySelector('textarea');
            const content = textarea.value.trim();

            if (!content) {
                textarea.classList.add('is-invalid');
                return;
            }

            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                handleError(new Error('CSRF Token not found'), '无法获取CSRF Token');
                return;
            }

            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(this)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(response.status === 400 ? '评论提交失败，请检查输入内容！' : '网络响应出错');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        // 清空表单
                        textarea.value = '';
                        textarea.classList.remove('is-invalid');

                        // 移除暂无评论提示
                        const noCommentsSection = safeQuerySelector('.text-center.p-5.bg-light.rounded-3');
                        if (noCommentsSection) {
                            try {
                                noCommentsSection.remove();
                            } catch (error) {
                                handleError(error, '移除暂无评论提示时发生错误');
                            }
                        }

                        // 创建新评论元素
                        const newComment = createCommentElement(data.comment);

// 查找评论列表容器
                        const commentsContainer = document.querySelector('.article-container .mt-5');
                        
                        // 检查新评论元素是否成功创建
                        if (!newComment) {
                            console.error('创建评论元素失败');
                            alert('创建评论失败，请刷新页面或稍后再试。');
                            return;
                        }

                        if (commentsContainer) {
                            // 如果评论列表容器存在
                            const firstComment = commentsContainer.querySelector('.comment-card');
                            if (firstComment) {
                                // 如果已有评论，将新评论插入到第一条评论前面
                                commentsContainer.insertBefore(newComment, firstComment);
                            } else {
                                // 如果没有评论，将新评论添加到容器的末尾
                                commentsContainer.appendChild(newComment);
                            }
                        } else {
                            // 如果评论列表容器不存在，提示用户或记录错误
                            console.error('无法找到评论列表容器');
                            alert('无法找到评论列表，无法插入新评论。请刷新页面或稍后再试。');
                        }

                        // 更新评论计数
                        const commentCountElement = document.querySelector('.fa-comment-dots')?.parentElement;
                        if (commentCountElement) {
                            const currentCount = parseInt(commentCountElement.textContent.match(/\d+/)[0]);
                            commentCountElement.innerHTML = `<i class="fas fa-comment-dots me-2"></i>全部评论 (${currentCount + 1})`;
                        }

                        // 显示成功提示
                        Swal.fire({
                            icon: 'success',
                            title: '评论发表成功',
                            showConfirmButton: false,
                            timer: 1500
                        });
                    } else {
                        throw new Error(data.message || '评论提交失败');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: '评论发表失败',
                        text: error.message || '请稍后重试',
                        confirmButtonText: '确定'
                    });
                });
        });
    }

    // 收藏按钮动画效果
    const favoriteForm = document.getElementById('favorite-form');
    const favoriteBtn = document.getElementById('favorite-btn');
    const favoriteCount = document.getElementById('favorite-count');

    if (favoriteForm) {
        favoriteForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // 添加动画效果
            const icon = favoriteBtn.querySelector('i');
            icon.classList.add('favorite-animation');

            // 使用通用函数获取CSRF令牌
            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                handleError(new Error('CSRF Token not found'), '无法获取CSRF Token', {autoClose: true});
                icon.classList.remove('favorite-animation');
                return;
            }
            
            // 发送异步请求
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(this)
            })
                .then(response => response.json())
                .then(data => {
                    // 更新收藏状态
                    if (data.is_favorite) {
                        favoriteBtn.classList.remove('btn-outline-danger');
                        favoriteBtn.classList.add('btn-danger');
                        favoriteBtn.innerHTML = '<i class="fas fa-heart me-1"></i> 取消收藏';
                    } else {
                        favoriteBtn.classList.remove('btn-danger');
                        favoriteBtn.classList.add('btn-outline-danger');
                        favoriteBtn.innerHTML = '<i class="far fa-heart me-1"></i> 收藏';
                    }

                    // 更新收藏数量
                    favoriteCount.textContent = data.favorite_count + ' 人收藏';

                    // 移除动画类
                    setTimeout(() => {
                        icon.classList.remove('favorite-animation');
                    }, 1300);
                })
                .catch(error => {
                    console.error('Error:', error);
                    // 移除动画类
                    icon.classList.remove('favorite-animation');
                });
        });
    }

    // 评论回复功能
    const replyBtns = document.querySelectorAll('.reply-btn');
    const cancelReplyBtns = document.querySelectorAll('.cancel-reply-btn');

    replyBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            // 隐藏其他所有回复表单
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form && form !== replyForm) {
                    form.style.display = 'none';
                }
            });

            // 切换当前回复表单的显示状态
            if (replyForm) {
                replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
            }
        });
    });

    cancelReplyBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (!replyForm) {
                console.warn(`Reply form not found for comment ${commentId}`);
                return;
            }
            replyForm.style.display = 'none';
            
            // 清空表单内容
            if (replyForm) {
                const textarea = replyForm.querySelector('textarea');
                if (textarea) {
                    textarea.value = '';
                    textarea.classList.remove('is-invalid');
                }
            }
        });
    });

    // 处理回复表单提交
    const replyForms = document.querySelectorAll('.reply-form form');
    replyForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const textarea = this.querySelector('textarea');
            const content = textarea.value.trim();

            if (!content) {
                textarea.classList.add('is-invalid');
                return;
            }

            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                handleError(new Error('CSRF Token not found'), '无法获取CSRF Token', {autoClose: true});
                return;
            }

            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(this)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.status === 400 ? '回复提交失败，请检查输入内容！' : '网络响应出错');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // 清空表单并隐藏
                    textarea.value = '';
                    textarea.classList.remove('is-invalid');
                    form.parentElement.style.display = 'none';

                    // 创建新回复元素
                    const newReply = createCommentElement(data.comment);
                    
                    // 检查新回复元素是否成功创建
                    if (!newReply) {
                        console.error('创建回复元素失败');
                        alert('创建回复失败，请刷新页面或稍后再试。');
                        return;
                    }
                    
                    try {
                        // 获取父评论ID，确保从正确的位置获取
                        const parentId = data.comment && data.comment.parent_id ? data.comment.parent_id : data.parent_id;
                        
                        if (!parentId) {
                            throw new Error('父评论ID不存在');
                        }
                        
                        const parentComment = document.getElementById(`comment-${parentId}`);
                        
                        // 检查父评论元素是否存在
                        if (!parentComment) {
                            throw new Error(`父评论元素不存在，ID: ${parentId}`);
                        }
                        
                        // 获取父评论作者名称
                        const parentAuthorElement = parentComment.querySelector('strong');
                        const parentAuthorName = parentAuthorElement ? parentAuthorElement.textContent : '用户';
                        
                        // 确保回复数据包含父评论信息
                        if (data.comment) {
                            data.comment.parent_id = parentId;
                            data.comment.parent_author_name = parentAuthorName;
                        }
                        
                        // 重新创建回复元素，确保使用更新后的数据
                        const newReply = createCommentElement(data.comment);
                        
                        // 安全地获取回复容器
                        const repliesContainer = parentComment.querySelector('.replies');
                        
                        if (repliesContainer) {
                            // 将新回复插入到回复容器的最前面
                            const firstReply = repliesContainer.querySelector('.reply');
                            if (firstReply) {
                                // 如果已有回复，将新回复插入到第一条回复前面
                                repliesContainer.insertBefore(newReply, firstReply);
                            } else {
                                // 如果没有回复，将新回复添加到容器的末尾
                                repliesContainer.appendChild(newReply);
                            }
                        } else {
                            // 如果还没有回复容器，创建一个
                            const newRepliesContainer = document.createElement('div');
                            newRepliesContainer.className = 'replies mt-3 ms-4 border-start ps-3';
                            newRepliesContainer.appendChild(newReply);
                            parentComment.appendChild(newRepliesContainer);
                        }
                    } catch (error) {
                        console.error('处理回复时出错:', error.message);
                        // 出错时，将回复作为普通评论添加到评论列表
                        const commentsContainer = document.querySelector('.article-container .mt-5');
                        if (commentsContainer) {
                            // 将新回复作为普通评论添加到评论列表的最前面
                            const firstComment = commentsContainer.querySelector('.comment-card');
                            if (firstComment) {
                                // 如果已有评论，将新回复插入到第一条评论前面
                                commentsContainer.insertBefore(newReply, firstComment);
                            } else {
                                // 如果没有评论，将新回复添加到容器的末尾
                                commentsContainer.appendChild(newReply);
                            }
                        } else {
                            console.error('无法找到评论容器，无法添加回复');
                        }
                    }

                    // 显示成功提示
                    Swal.fire({
                        icon: 'success',
                        title: '回复发表成功',
                        showConfirmButton: false,
                        timer: 1500
                    });
                } else {
                    throw new Error(data.message || '回复提交失败');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: '回复发表失败',
                    text: error.message || '请稍后重试',
                    confirmButtonText: '确定'
                });
            });
        });
    });

    // 标签和分类筛选动画
    const tagBadges = document.querySelectorAll('.tag-badge');
    const categoryBadges = document.querySelectorAll('.category-badge');

    const addHoverEffect = (elements) => {
        elements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.transform = 'translateY(-2px)';
                element.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            });

            element.addEventListener('mouseleave', () => {
                element.style.transform = '';
                element.style.boxShadow = '';
            });
        });
    };

    addHoverEffect(tagBadges);
    addHoverEffect(categoryBadges);

    // 评论删除功能
    document.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('delete-comment-btn')) {
            e.preventDefault();
            const commentId = e.target.dataset.commentId;
            const commentElement = document.getElementById(`comment-${commentId}`);
            const deleteBtn = e.target;

            if (!commentElement) {
                alert('评论元素不存在，可能已被删除');
                return;
            }

            if (confirm('确定要删除这条评论吗？')) {
                // 添加加载状态
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 删除中...';
                commentElement.style.opacity = '0.5';

                // 使用通用函数获取CSRF令牌
                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    handleError(new Error('CSRF Token not found'), '无法获取CSRF Token', {autoClose: true});
                    // 恢复评论元素状态
                    commentElement.style.opacity = '1';
                    deleteBtn.disabled = false;
                    deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> 删除';
                    return;
                }
                
                fetch(`/article/comment/delete/${commentId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(response.status === 403 ? '您没有权限删除此评论' : '网络响应出错');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.status === 'success') {
                            // 添加淡出动画
                            commentElement.style.transition = 'all 0.3s ease';
                            commentElement.style.opacity = '0';
                            commentElement.style.transform = 'translateY(-10px)';

                            setTimeout(() => {
                                commentElement.remove();
                                // 更新评论计数
                                const commentCountElement = document.querySelector('.fa-comment-dots')?.parentElement;
                                if (commentCountElement) {
                                    const countText = commentCountElement.textContent;
                                    const currentCount = parseInt(countText.match(/\d+/)?.[0] || '0');
                                    const newCount = Math.max(0, currentCount - 1);

                                    // 无论 newCount 是否为 0，都保留图标和文本
                                    commentCountElement.innerHTML = `<i class="fas fa-comment-dots me-2"></i>全部评论 (${newCount})`;

                                    // 如果 newCount 为 0，显示额外的提示信息
                                    if (newCount === 0) {
                                        const noCommentsDiv = document.createElement('div');
                                        noCommentsDiv.className = 'text-center p-5 bg-light rounded-3';
                                        noCommentsDiv.innerHTML = `
                                    <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                                    <h5 class="text-muted">暂无评论</h5>
                                    <p class="text-muted">成为第一个评论的人吧！</p>
                                `;

                                        // 将提示信息插入到评论计数元素的下方
                                        commentCountElement.parentNode.insertBefore(noCommentsDiv, commentCountElement.nextSibling);
                                    } else {
                                        // 如果有评论，移除“暂无评论”的提示（如果存在）
                                        const noCommentsDiv = commentCountElement.nextSibling;
                                        if (noCommentsDiv && noCommentsDiv.classList.contains('text-center') && noCommentsDiv.classList.contains('bg-light')) {
                                            noCommentsDiv.remove();
                                        }
                                    }
                                }

                            }, 200);

                            // 使用更友好的成功提示
                            const Toast = Swal.mixin({
                                toast: true,
                                position: 'top-end',
                                showConfirmButton: false,
                                timer: 3000,
                                timerProgressBar: true
                            });
                            Toast.fire({
                                icon: 'success',
                                title: data.message || '评论已成功删除'
                            });
                        } else {
                            throw new Error(data.message || '删除评论失败');
                        }
                    })
                    .catch(error => {
                        console.error('删除评论错误:', error);
                        // 恢复评论元素状态
                        commentElement.style.opacity = '1';
                        deleteBtn.disabled = false;
                        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> 删除';

                        // 使用更友好的错误提示
                        Swal.fire({
                            icon: 'error',
                            title: '删除失败',
                            text: error.message || '删除评论时发生错误，请稍后重试',
                            confirmButtonText: '确定'
                        });
                    });
            }
        }
    });
});


// 创建评论元素的函数
function createCommentElement(comment) {
    if (!comment || typeof comment !== 'object') {
        console.error('Invalid comment object');
        return null;
    }

    // 确保所有必需的属性都存在
    const defaultComment = {
        id: Date.now(), // 如果没有ID，使用时间戳作为临时ID
        author_name: '匿名用户',
        content: '',
        created_time: '刚刚',
        is_author: false,
        can_delete: false,
        parent_id: null,  // 添加父评论ID属性，用于判断是否为回复
        parent_author_name: null  // 添加父评论作者名称
    };
    
    // 合并默认值和实际评论数据
    comment = { ...defaultComment, ...comment };
    
    // 格式化时间 - 使用新增的格式化函数确保一致性
    const formattedTime = formatTime(comment.created_time);
    
    // 判断是否为回复
    const isReply = comment.parent_id !== null;
    
    if (isReply) {
        // 创建回复元素 - 使用与模板相同的结构
        const replyDiv = document.createElement('div');
        replyDiv.className = 'reply mb-3';
        replyDiv.id = `comment-${comment.id}`;
        
        replyDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong class="text-success">${comment.author_name || '匿名用户'}</strong>
                    ${comment.is_author ? '<span class="badge bg-success ms-1">作者</span>' : ''}
                    <span class="text-muted">回复了</span>
                    <strong>${comment.parent_author_name || '用户'}</strong>
                </div>
                <small class="text-muted">${formattedTime}</small>
            </div>
            <div class="mt-2">${comment.content || ''}</div>
        `;
        
        return replyDiv;
    }
    
    // 以下是普通评论的创建逻辑
    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment-card mb-4'; // 添加底部间距
    commentDiv.id = `comment-${comment.id}`;

    const headerDiv = document.createElement('div');
    headerDiv.className = 'comment-header';

    const headerContent = `
        <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <i class="fas fa-user-circle me-2 text-success"></i>
                <strong>${comment.author_name || '匿名用户'}</strong>
                ${comment.is_author ? '<span class="badge bg-success ms-2">作者</span>' : ''}
            </div>
            <div class="text-muted small">
                <i class="fas fa-clock me-1"></i>
                ${formattedTime}
            </div>
        </div>
    `;
    headerDiv.innerHTML = headerContent;

    // 创建评论内容和操作按钮的容器
    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'comment-body';

    // 添加评论内容
    bodyDiv.innerHTML = `
        <div class="mb-3">${comment.content || ''}</div>
    `;


    // 添加操作按钮
    bodyDiv.innerHTML += `
        <div class="mt-3 text-end">
            <button class="btn btn-sm btn-outline-secondary rounded-pill reply-btn" data-comment-id="${comment.id}">
                <i class="fas fa-reply me-1"></i>回复
            </button>
            ${comment.can_delete ? `
                <button class="btn btn-sm btn-outline-danger rounded-pill delete-comment-btn ms-2" data-comment-id="${comment.id}">
                    <i class="fas fa-trash-alt me-1"></i>删除
                </button>
            ` : ''}
        </div>
    `;

    // 获取CSRF token，添加错误处理
    let csrfToken = '';
    try {
        const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfElement) {
            csrfToken = csrfElement.value;
        } else {
            console.warn('CSRF token element not found');
        }
    } catch (error) {
        console.error('Error getting CSRF token:', error);
    }

    // 添加回复表单
    bodyDiv.innerHTML += `
        <div class="reply-form mt-3" id="reply-form-${comment.id}" style="display: none;">
            <form method="post" action="" class="needs-validation" novalidate>
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                <input type="hidden" name="parent_id" value="${comment.id}">
                <div class="form-group mb-2">
                    <textarea name="content" class="form-control" placeholder="回复 ${comment.author_name || ''}..." style="height: 80px; border-radius: 10px;"></textarea>
                </div>
                <div class="text-end">
                    <button type="button" class="btn btn-sm btn-outline-secondary rounded-pill me-2 cancel-reply-btn" data-comment-id="${comment.id}">
                        取消
                    </button>
                    <button type="submit" class="btn btn-sm btn-success rounded-pill">
                        <i class="fas fa-paper-plane me-1"></i>提交回复
                    </button>
                </div>
            </form>
        </div>
    `;

    commentDiv.appendChild(headerDiv);
    commentDiv.appendChild(bodyDiv);

    // 为新创建的回复按钮添加事件监听器，添加错误处理
    const replyBtn = bodyDiv.querySelector('.reply-btn');
    if (replyBtn) {
        replyBtn.addEventListener('click', function() {
            try {
                const replyForm = document.getElementById(`reply-form-${comment.id}`);
                if (!replyForm) {
                    console.warn(`Reply form not found for comment ${comment.id}`);
                    return;
                }
                
                // 隐藏其他所有回复表单
                document.querySelectorAll('.reply-form').forEach(form => {
                    if (form && form !== replyForm) {
                        form.style.display = 'none';
                    }
                });

                // 切换当前回复表单的显示状态
                replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
            } catch (error) {
                console.error(`处理回复按钮点击时出错: ${error.message}`);
            }
        });
    }

    // 为新创建的取消回复按钮添加事件监听器
    const cancelReplyBtn = bodyDiv.querySelector('.cancel-reply-btn');
    if (cancelReplyBtn) {
        cancelReplyBtn.addEventListener('click', function() {
            const replyForm = document.getElementById(`reply-form-${comment.id}`);
            if (!replyForm) {
                console.warn(`Reply form not found for comment ${comment.id}`);
                return;
            }
            replyForm.style.display = 'none';
            
            // 清空表单内容
            const textarea = replyForm.querySelector('textarea');
            if (textarea) {
                textarea.value = '';
                textarea.classList.remove('is-invalid');
            }
        });
    }

    return commentDiv;
}

// 格式化时间工具函数 - 保证时间格式一致性
const formatTime = (timeStr) => {
    if (!timeStr) return '刚刚';
    
    // 统一时间格式为 "MM-DD HH:MM" 或 "X分钟前"
    try {
        const date = new Date(timeStr);
        if (isNaN(date.getTime())) {
            // 如果不是有效日期，直接返回原始字符串
            return timeStr;
        }
        
        const now = new Date();
        
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        // 如果是当前年份，不显示年份
        const currentYear = new Date().getFullYear();
        return `${month}-${day} ${hours}:${minutes}`;
    } catch (error) {
        console.warn('时间格式化错误:', error);
        return timeStr;
    }
};