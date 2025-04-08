/**
 * 页面性能增强脚本
 * 动态减少动画效果，优化表单渲染
 */
(function() {
    'use strict';
    
    // 判断设备性能
    const isLowPerformance = 
        window.matchMedia('(prefers-reduced-motion: reduce)').matches || 
        navigator.hardwareConcurrency < 4 || 
        /Mobile|Android/.test(navigator.userAgent);
    
    // 页面加载计时
    const startTime = performance.now();
    
    // DOM加载完成后执行的优化
    document.addEventListener('DOMContentLoaded', function() {
        // 减少动画效果
        if (isLowPerformance) {
            disableAnimations();
        }
        
        // 优化表单渲染
        optimizeForms();
        
        // 禁用不必要的jQuery动画
        if (window.jQuery) {
            jQuery.fx.off = isLowPerformance;
        }
        
        // 记录加载时间
        const loadTime = performance.now() - startTime;
        console.log(`DOM加载时间: ${Math.round(loadTime)}ms`);
        
        // 如果加载时间超过1000ms，减少后续动画
        if (loadTime > 1000) {
            disableAnimations();
        }
    });
    
    // 完全禁用动画效果
    function disableAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            * {
                transition-duration: 0.01ms !important;
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
            }
            
            .animate-fadeInUp, .animate-fadeIn, .fade-in, 
            .animate-pulse, .scroll-fade, .favorite-animation {
                animation: none !important;
                opacity: 1 !important;
                transform: none !important;
            }
        `;
        document.head.appendChild(style);
        
        // 立即显示所有需要动画的元素
        document.querySelectorAll('.scroll-fade, .animate-fadeInUp, .animate-fadeIn').forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
        });
    }
    
    // 优化表单渲染
    function optimizeForms() {
        // 简化表单验证，减少不必要的DOM操作
        document.querySelectorAll('form').forEach(form => {
            // 使用原生验证，避免额外的验证动画
            form.setAttribute('novalidate', '');
            
            form.addEventListener('submit', function(e) {
                const invalidFields = this.querySelectorAll(':invalid');
                
                if (invalidFields.length) {
                    e.preventDefault();
                    
                    // 仅聚焦第一个无效字段，避免过多的DOM操作
                    invalidFields[0].focus();
                    
                    // 使用简单的视觉反馈而不是动画
                    invalidFields.forEach(field => {
                        field.style.borderColor = '#dc3545';
                    });
                }
            }, {passive: false});
            
            // 重置验证样式
            form.querySelectorAll('input, textarea, select').forEach(field => {
                field.addEventListener('input', function() {
                    this.style.borderColor = '';
                }, {passive: true});
            });
        });
    }
    
    // 页面完全加载后执行
    window.addEventListener('load', function() {
        const totalLoadTime = performance.now() - startTime;
        console.log(`页面完全加载时间: ${Math.round(totalLoadTime)}ms`);
        
        // 减少加载完成后的动画效果
        if (totalLoadTime > 2000) {
            disableAnimations();
            console.log('由于加载时间过长，已禁用动画效果');
        }
    });
})();
