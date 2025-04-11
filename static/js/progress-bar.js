/**
 * 页面加载进度条
 * 为用户提供更好的加载反馈
 */

class PageProgressBar {
    constructor() {
        this.progress = 0;
        this.createElements();
        this.bindEvents();
    }
    
    createElements() {
        // 创建进度条容器
        const container = document.createElement('div');
        container.id = 'progress-container';
        
        // 创建进度条
        const bar = document.createElement('div');
        bar.id = 'progress-bar';
        
        container.appendChild(bar);
        document.body.appendChild(container);
        
        // 创建页面加载器
        const pageLoader = document.createElement('div');
        pageLoader.className = 'page-loader';
        pageLoader.innerHTML = `
            <div class="loader-content">
                <div class="spinner"></div>
                <p class="loader-message">正在加载，请稍候...</p>
            </div>
        `;
        
        document.body.appendChild(pageLoader);
        
        this.bar = bar;
        this.pageLoader = pageLoader;
    }
    
    bindEvents() {
        // 页面加载事件
        window.addEventListener('load', () => {
            this.setProgress(100);
            this.hideLoader();
        });
        
        // 监听Ajax请求
        this.setupAjaxListeners();
        
        // 页面离开事件
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.setProgress(0);
            }
        });
        
        // 模拟初始加载进度
        this.simulateProgress();
    }
    
    setupAjaxListeners() {
        // 拦截所有fetch请求
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            this.setProgress(30);
            try {
                const response = await originalFetch(...args);
                this.setProgress(100);
                return response;
            } catch (error) {
                this.setProgress(100);
                throw error;
            }
        };
        
        // 拦截所有XMLHttpRequest
        const originalXhrOpen = XMLHttpRequest.prototype.open;
        const self = this; // 使用变量保存this引用
        
        XMLHttpRequest.prototype.open = function(...args) {
            this.addEventListener('loadstart', function() {
                self.setProgress(30);
            });
            
            this.addEventListener('load', function() {
                self.setProgress(100);
            });
            
            this.addEventListener('error', function() {
                self.setProgress(100);
            });
            
            return originalXhrOpen.apply(this, args);
        };
    }
    
    simulateProgress() {
        this.setProgress(30);
        
        setTimeout(() => {
            this.setProgress(50);
        }, 200);
        
        setTimeout(() => {
            this.setProgress(70);
        }, 500);
    }
    
    setProgress(value) {
        this.progress = value;
        
        if (this.bar) {
            this.bar.style.width = `${value}%`;
        }
        
        // 进度达到100时，延迟隐藏进度条
        if (value === 100) {
            setTimeout(() => {
                this.bar.style.width = '0';
            }, 500);
        }
    }
    
    hideLoader() {
        if (this.pageLoader) {
            this.pageLoader.classList.add('loader-hidden');
            
            // 等待动画结束后移除
            setTimeout(() => {
                this.pageLoader.remove();
            }, 300);
        }
    }
    
    // 手动显示加载器
    showLoader(message = '处理中...') {
        if (this.pageLoader) {
            const messageEl = this.pageLoader.querySelector('.loader-message');
            if (messageEl) {
                messageEl.textContent = message;
            }
            
            this.pageLoader.classList.remove('loader-hidden');
        }
    }
}

// 页面加载完成后初始化进度条
document.addEventListener('DOMContentLoaded', function() {
    window.pageProgress = new PageProgressBar();
});
