/**
 * 页面性能优化脚本
 * 用于提高页面加载和渲染速度
 */

(function() {
    'use strict';
    
    // 记录性能指标
    const perfData = {
        startTime: performance.now(),
        domContentLoaded: 0,
        fullyLoaded: 0,
        firstPaint: 0,
        resourcesLoaded: []
    };
    
    // 在DOM内容加载完成时记录时间
    document.addEventListener('DOMContentLoaded', function() {
        perfData.domContentLoaded = performance.now() - perfData.startTime;
        console.log(`DOM内容加载完成: ${Math.round(perfData.domContentLoaded)}ms`);
        
        // 开始延迟加载资源
        initResourceDelayLoad();
    });
    
    // 在页面完全加载后记录时间
    window.addEventListener('load', function() {
        perfData.fullyLoaded = performance.now() - perfData.startTime;
        console.log(`页面完全加载: ${Math.round(perfData.fullyLoaded)}ms`);
        
        // 分析资源加载情况
        analyzeResourceLoading();
    });
    
    // 初始化延迟加载
    function initResourceDelayLoad() {
        // 使用 Intersection Observer 延迟加载图片
        if ('IntersectionObserver' in window) {
            const imgObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            // 记录加载开始时间
                            const startTime = performance.now();
                            
                            // 设置图片加载完成的回调
                            img.onload = function() {
                                perfData.resourcesLoaded.push({
                                    type: 'image',
                                    url: img.src,
                                    loadTime: performance.now() - startTime
                                });
                            };
                            
                            // 加载图片
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        imgObserver.unobserve(img);
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
        } else {
            // 回退方案：立即加载所有图片
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
        
        // 延迟加载非必要的CSS和JS
        setTimeout(() => {
            loadDeferredResources();
        }, 100);
    }
    
    // 加载延迟的资源
    function loadDeferredResources() {
        // 加载延迟CSS
        document.querySelectorAll('link[data-href]').forEach(link => {
            link.setAttribute('href', link.getAttribute('data-href'));
            link.removeAttribute('data-href');
        });
        
        // 加载延迟JS
        document.querySelectorAll('script[data-src]').forEach(script => {
            script.setAttribute('src', script.getAttribute('data-src'));
            script.removeAttribute('data-src');
        });
    }
    
    // 分析资源加载情况
    function analyzeResourceLoading() {
        // 获取性能条目
        if (window.performance && window.performance.getEntriesByType) {
            const resources = window.performance.getEntriesByType('resource');
            
            // 按资源类型分组
            const resourcesByType = resources.reduce((acc, resource) => {
                const type = getResourceType(resource.name);
                if (!acc[type]) {
                    acc[type] = [];
                }
                acc[type].push({
                    name: resource.name,
                    duration: resource.duration,
                    size: resource.transferSize || 0
                });
                return acc;
            }, {});
            
            // 计算每种类型的总加载时间和大小
            Object.keys(resourcesByType).forEach(type => {
                const typeResources = resourcesByType[type];
                const totalDuration = typeResources.reduce((sum, r) => sum + r.duration, 0);
                const totalSize = typeResources.reduce((sum, r) => sum + r.size, 0);
                
                console.log(`${type} 资源 (${typeResources.length}个):`);
                console.log(`  总加载时间: ${Math.round(totalDuration)}ms`);
                console.log(`  总大小: ${formatBytes(totalSize)}`);
                
                // 找出加载时间最长的资源
                if (typeResources.length > 0) {
                    const slowest = typeResources.sort((a, b) => b.duration - a.duration)[0];
                    console.log(`  最慢资源: ${slowest.name} (${Math.round(slowest.duration)}ms)`);
                }
            });
        }
    }
    
    // 判断资源类型
    function getResourceType(url) {
        if (url.match(/\.css(\?|$)/)) return 'CSS';
        if (url.match(/\.js(\?|$)/)) return 'JavaScript';
        if (url.match(/\.(png|jpg|jpeg|gif|webp|svg)(\?|$)/)) return 'Image';
        if (url.match(/\.(woff|woff2|ttf|eot)(\?|$)/)) return 'Font';
        return 'Other';
    }
    
    // 格式化字节大小
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 预加载修复工具
    if (!('IntersectionObserver' in window)) {
        // 如果浏览器不支持 Intersection Observer，加载polyfill
        const script = document.createElement('script');
        script.src = 'https://polyfill.io/v3/polyfill.min.js?features=IntersectionObserver';
        document.head.appendChild(script);
    }
    
    // 修复表单初始化问题
    window.fixFormInitializationErrors = function() {
        document.querySelectorAll('form').forEach(form => {
            // 检查表单实例初始化问题
            if (form.classList.contains('needs-validation')) {
                form.addEventListener('submit', function(event) {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            }
        });
    };
    
    // DOM加载完成后执行
    document.addEventListener('DOMContentLoaded', function() {
        // 修复表单初始化问题
        window.fixFormInitializationErrors();
    });
})();
