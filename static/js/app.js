/**
 * 农业智库应用核心JS
 * 用于性能优化与用户体验提升
 */

document.addEventListener('DOMContentLoaded', function() {
    // 性能计时开始
    const startTime = performance.now();
    
    // 初始化所有组件
    initializeComponents();
    
    // 延迟加载图片和内容
    setupLazyLoading();
    
    // 设置渐进增强的交互体验
    enhanceInteractions();
    
    // 监听网络状态
    monitorNetworkStatus();
    
    // 性能计时结束
    window.addEventListener('load', function() {
        const loadTime = Math.round(performance.now() - startTime);
        console.log(`页面完全加载耗时: ${loadTime}ms`);
        
        // 发送性能数据（可以在后续集成分析系统）
        // sendPerformanceMetrics(loadTime);
    });
});

/**
 * 初始化所有组件
 */
function initializeComponents() {
    // 初始化工具提示
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // 初始化弹出框
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });
    
    // 初始化回到顶部按钮
    initBackToTop();
    
    // 初始化导航栏滚动效果
    initNavbarScroll();
}

/**
 * 设置图片和内容的延迟加载
 */
function setupLazyLoading() {
    // 使用 Intersection Observer API 延迟加载图片
    if ('IntersectionObserver' in window) {
        const imgObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });

        // 观察所有懒加载图片
        document.querySelectorAll('img[data-src]').forEach(img => {
            imgObserver.observe(img);
        });
        
        // 延迟加载内容
        const contentObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '30px 0px',
            threshold: 0.1
        });
        
        document.querySelectorAll('.scroll-fade').forEach(el => {
            contentObserver.observe(el);
        });
    } else {
        // 针对不支持 Intersection Observer 的浏览器的回退方案
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
        });
        document.querySelectorAll('.scroll-fade').forEach(el => {
            el.classList.add('visible');
        });
    }
}

/**
 * 增强用户交互体验
 */
function enhanceInteractions() {
    // 表单输入增强
    document.querySelectorAll('input, textarea').forEach(input => {
        // 添加焦点动画
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
        
        // 输入验证动画
        if (input.required) {
            input.addEventListener('invalid', function() {
                this.classList.add('animate-shake');
                setTimeout(() => {
                    this.classList.remove('animate-shake');
                }, 600);
            });
        }
    });
    
    // 链接点击动画
    document.querySelectorAll('a:not(.navbar-brand):not(.nav-link)').forEach(link => {
        link.addEventListener('click', function(e) {
            // 只对站内链接添加过渡效果
            if (this.hostname === window.location.hostname && !this.dataset.noTransition) {
                const href = this.getAttribute('href');
                if (href.charAt(0) === '#') return; // 不对锚点链接添加效果
                
                e.preventDefault();
                document.body.classList.add('page-transition-out');
                
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            }
        });
    });
    
    // 添加页面进入动画
    document.body.classList.add('page-transition-in');
    setTimeout(() => {
        document.body.classList.remove('page-transition-in');
    }, 500);
}

/**
 * 初始化回到顶部按钮
 */
function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * 初始化导航栏滚动效果
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
}

/**
 * 监控网络状态并提供离线支持
 */
function monitorNetworkStatus() {
    function updateOnlineStatus() {
        const status = navigator.onLine ? 'online' : 'offline';
        
        if (status === 'offline') {
            // 当网络断开时通知用户
            showToast('网络连接已断开，部分功能可能不可用。', 'warning');
        } else {
            // 当网络恢复时通知用户
            if (document.querySelector('.toast-container')) {
                showToast('网络连接已恢复。', 'success');
            }
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
}

/**
 * 显示通知提示
 * @param {string} message - 提示消息
 * @param {string} type - 提示类型 (success, warning, danger, info)
 */
function showToast(message, type = 'info') {
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast show animate-fadeInUp`;
    toast.id = toastId;
    toast.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <strong class="me-auto">农业智库</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // 3秒后自动关闭
    setTimeout(() => {
        toast.classList.add('animate-fadeOut');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

/**
 * 获取CSRF令牌
 * @returns {string} CSRF token
 */
function getCsrfToken() {
    const csrfCookie = document.cookie.match(/csrftoken=([^;]+)/);
    return csrfCookie ? csrfCookie[1] : '';
}

/**
 * 发送AJAX请求
 * @param {string} url - 请求URL
 * @param {Object} options - 请求配置
 * @returns {Promise} 请求Promise
 */
async function sendRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`请求失败: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    } catch (error) {
        console.error('请求错误:', error);
        throw error;
    }
}
