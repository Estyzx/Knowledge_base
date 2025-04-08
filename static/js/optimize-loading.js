/**
 * 页面加载优化脚本
 * 减少动画和优化资源加载
 */
(function() {
    'use strict';
    
    // 检测浏览器性能
    const lowPerformance = window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
                          navigator.hardwareConcurrency < 4 ||
                          /Mobile|Android/.test(navigator.userAgent);
    
    // 基于页面加载性能的配置
    const config = {
        // 禁用或减少不必要的动画
        animations: !lowPerformance,
        // 延迟加载非关键资源
        lazyLoad: true,
        // 减少CSS动画
        reduceCSSAnimations: lowPerformance,
        // 预加载关键资源
        preloadCritical: true
    };
    
    // 优化CSS动画 - 如果设备性能较差，停用大部分动画
    function optimizeCSSAnimations() {
        if (config.reduceCSSAnimations) {
            // 创建样式覆盖
            const style = document.createElement('style');
            style.textContent = `
                .animate-fadeInUp, .animate-fadeIn, .fade-in, 
                .animate-pulse, .hover-grow, .scroll-fade {
                    animation: none !important;
                    opacity: 1 !important;
                    transform: none !important;
                    transition: none !important;
                }
                
                /* 保留必要的交互反馈动画 */
                .form-control:focus, .btn:hover {
                    transition: all 0.2s ease !important;
                }
                
                /* 减少悬停效果 */
                .hover-card:hover, .content-card:hover {
                    transform: none !important;
                    box-shadow: var(--shadow-md) !important;
                }
            `;
            document.head.appendChild(style);
            
            // 立即显示所有需要淡入的元素
            document.querySelectorAll('.scroll-fade, .animate-fadeInUp, .animate-fadeIn').forEach(el => {
                el.classList.add('visible');
                el.style.opacity = '1';
            });
        }
    }
    
    // 延迟加载非关键资源
    function setupLazyLoading() {
        if (!config.lazyLoad) return;
        
        // 使用原生懒加载属性
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.setAttribute('loading', 'lazy');
            img.src = img.dataset.src;
        });
        
        // 延迟加载后台统计等非关键脚本
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.querySelectorAll('script[data-src]').forEach(script => {
                    const newScript = document.createElement('script');
                    newScript.src = script.dataset.src;
                    document.body.appendChild(newScript);
                });
            }, 1000);
        });
    }
    
    // 优化动态加载的表单
    function optimizeForms() {
        // 简化表单处理逻辑
        document.querySelectorAll('form').forEach(form => {
            if (form.classList.contains('needs-validation')) {
                // 使用更简洁的验证处理
                form.addEventListener('submit', function(e) {
                    if (!this.checkValidity()) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // 找到第一个无效字段并聚焦
                        const invalidField = this.querySelector(':invalid');
                        if (invalidField) {
                            invalidField.focus();
                        }
                    }
                    
                    this.classList.add('was-validated');
                }, {passive: true});
            }
        });
    }
    
    // 禁用或简化非核心jQuery动画
    function optimizeJQueryAnimations() {
        if (window.jQuery) {
            // 简化jQuery动画
            jQuery.fx.off = lowPerformance;
            
            // 覆盖slideUp/slideDown为更快的实现
            const originalSlideDown = jQuery.fn.slideDown;
            const originalSlideUp = jQuery.fn.slideUp;
            
            jQuery.fn.slideDown = function(duration, callback) {
                if (lowPerformance || duration < 200) {
                    this.show();
                    if (typeof callback === 'function') callback.call(this);
                    return this;
                }
                return originalSlideDown.call(this, Math.min(duration, 200), callback);
            };
            
            jQuery.fn.slideUp = function(duration, callback) {
                if (lowPerformance || duration < 200) {
                    this.hide();
                    if (typeof callback === 'function') callback.call(this);
                    return this;
                }
                return originalSlideUp.call(this, Math.min(duration, 200), callback);
            };
        }
    }
    
    // 预加载关键资源
    function preloadCriticalResources() {
        if (!config.preloadCritical) return;
        
        const criticalResources = [
            '/static/css/animations.css',
            '/static/js/app.js'
        ];
        
        criticalResources.forEach(resource => {
            const preload = document.createElement('link');
            preload.rel = 'preload';
            preload.href = resource;
            preload.as = resource.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(preload);
        });
    }
    
    // 初始化加载优化
    function init() {
        // 开始记录性能时间
        const startTime = performance.now();
        
        // 预加载关键资源
        preloadCriticalResources();
        
        // 优化CSS动画，减少重绘和重排
        optimizeCSSAnimations();
        
        // 设置图片和脚本的延迟加载
        setupLazyLoading();
        
        // 优化表单处理
        document.addEventListener('DOMContentLoaded', optimizeForms);
        
        // 优化jQuery动画
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', optimizeJQueryAnimations);
        } else {
            optimizeJQueryAnimations();
        }
        
        // 记录初始化完成时间
        console.log(`加载优化完成: ${Math.round(performance.now() - startTime)}ms`);
    }
    
    // 立即运行初始化
    init();
    
    // 为外部提供接口
    window.optimizeLoading = {
        config: config,
        optimizeForms: optimizeForms,
        optimizeCSSAnimations: optimizeCSSAnimations
    };
})();
