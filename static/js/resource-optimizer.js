/**
 * 资源优化器
 * 针对性能分析结果优化资源加载
 */
(function() {
    'use strict';
    
    // 优化配置
    const config = {
        // 资源加载优先级
        priorities: {
            critical: [], // 关键资源
            high: [       // 高优先级
                'bootstrap.min.css',
                'performance.js',
                'app.js'
            ],
            medium: [     // 中优先级
                'all.min.css',
                'jquery-3.6.0.min.js'
            ],
            low: [        // 低优先级
                'sweetalert2.all.min.js',
                'sweetalert2.min.css',
                'white/'
            ],
            defer: [      // 可延迟加载
                'bootstrap.bundle.min.js'
            ]
        },
        
        
        // 本地缓存配置
        cache: {
            enabled: true,
            expiration: 24 * 60 * 60 * 1000, // 24小时
        },
        
        // 图片优化配置
        images: {
            lazyLoad: true,
            lazyThreshold: 300,
            prefetch: [
                '/static/logo.svg',
                '/static/white/0@2x.png',
                '/static/white/1@2x.png'
            ]
        }
    };
    
    // 启动优化
    function init() {
        // 记录开始时间
        const startTime = performance.now();
        
        
        // 优化资源加载顺序
        prioritizeResources();
        
        // 预连接到关键域
        setupPreconnect();
        
        // 图片懒加载
        setupImageLazyLoading();
        
        // 延迟非关键JavaScript
        deferNonCriticalJS();
        
        // 预缓存关键资源
        precacheResources();
        
        // 清理无用的DOM元素和监听器
        cleanupDOM();
        
        // 记录优化完成时间
        console.log(`资源优化完成: ${Math.round(performance.now() - startTime)}ms`);
    }
    
    
    // 优化资源加载顺序
    function prioritizeResources() {
        // 处理已加载的资源
        document.querySelectorAll('link[href], script[src]').forEach(element => {
            const urlAttr = element.hasAttribute('href') ? 'href' : 'src';
            const url = element.getAttribute(urlAttr);
            
            // 设置资源加载优先级
            let priority = 'auto';
            
            // 检查资源应该使用哪个优先级
            for (const [prio, patterns] of Object.entries(config.priorities)) {
                if (patterns.some(pattern => url.includes(pattern))) {
                    priority = prio === 'critical' ? 'high' : 
                              prio === 'high' ? 'high' : 
                              prio === 'medium' ? 'medium' : 'low';
                    break;
                }
            }
            
            // 应用优先级
            if (priority !== 'auto') {
                element.setAttribute('fetchpriority', priority);
            }
            
            // 对于低优先级资源，添加延迟加载
            if (priority === 'low' && element.tagName === 'LINK') {
                element.setAttribute('media', 'print');
                element.setAttribute('onload', "this.media='all'");
            }
            
            // 对于延迟加载的JS，使用defer
            if (element.tagName === 'SCRIPT' && 
                config.priorities.defer.some(pattern => url.includes(pattern))) {
                element.async = false;
                element.defer = true;
            }
        });
    }
    
    // 设置预连接
    function setupPreconnect() {
        const domains = [
            'https://cdn.jsdelivr.net',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com'
        ];
        
        domains.forEach(domain => {
            if (!document.querySelector(`link[rel="preconnect"][href="${domain}"]`)) {
                const link = document.createElement('link');
                link.rel = 'preconnect';
                link.href = domain;
                link.crossOrigin = 'anonymous';
                document.head.appendChild(link);
            }
        });
    }
    
    // 图片懒加载设置
    function setupImageLazyLoading() {
        if (!config.images.lazyLoad) return;
        
        const images = document.querySelectorAll('img:not([loading])');
        
        images.forEach(img => {
            // 不在视口中的图片使用懒加载
            if (!isElementInViewport(img)) {
                img.setAttribute('loading', 'lazy');
                
                // 如果没有 src 但有 data-src，为原生懒加载做准备
                if (!img.src && img.dataset.src) {
                    // 创建低质量的占位图
                    if (img.width > 0 && img.height > 0) {
                        img.src = generatePlaceholder(img.width, img.height);
                    }
                }
            }
        });
        
        // 预加载关键图片
        if (config.images.prefetch && config.images.prefetch.length) {
            config.images.prefetch.forEach(imgPath => {
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = imgPath;
                link.as = 'image';
                document.head.appendChild(link);
            });
        }
    }
    
    // 延迟非关键JS
    function deferNonCriticalJS() {
        document.querySelectorAll('script[src]:not([defer]):not([async])').forEach(script => {
            const src = script.getAttribute('src');
            
            // 如果脚本不是高优先级且不在关键路径上
            if (!config.priorities.critical.some(pattern => src.includes(pattern)) &&
                !config.priorities.high.some(pattern => src.includes(pattern))) {
                
                // 创建新的延迟加载脚本
                const deferScript = document.createElement('script');
                deferScript.src = src;
                deferScript.defer = true;
                
                // 替换原脚本
                script.parentNode.replaceChild(deferScript, script);
            }
        });
    }
    
    // 检查元素是否在视口中
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // 生成低质量占位图
    function generatePlaceholder(width, height) {
        // 创建小型灰色占位图
        const canvas = document.createElement('canvas');
        canvas.width = 10;
        canvas.height = 10 * (height / width);
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#f0f0f0';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.1);
    }
    
    // 预缓存关键资源
    function precacheResources() {
        if (!config.cache.enabled || !('caches' in window)) return;
        
        // 预缓存重要的静态资源
        if (navigator.serviceWorker && navigator.serviceWorker.controller) {
            const resources = [
                '/static/css/animations.css',
                '/static/js/app.js',
                '/static/js/progress-bar.js'
            ];
            
            navigator.serviceWorker.controller.postMessage({
                action: 'cache',
                urls: resources
            });
        }
    }
    
    // 清理DOM
    function cleanupDOM() {
        // 删除不必要的空白节点来减少DOM大小
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            { acceptNode: node => /^\s+$/.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT }
        );
        
        const nodesToRemove = [];
        while (walker.nextNode()) {
            nodesToRemove.push(walker.currentNode);
        }
        
        nodesToRemove.forEach(node => {
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        });
        
        // 删除空的评论节点
        const commentWalker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_COMMENT,
            null
        );
        
        const commentNodesToRemove = [];
        while (commentWalker.nextNode()) {
            commentNodesToRemove.push(commentWalker.currentNode);
        }
        
        commentNodesToRemove.forEach(node => {
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        });
    }
    
    // 监听DOM加载
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 暴露公共API
    window.resourceOptimizer = {
        config: config,
        refreshOptimizations: init
    };
})();
