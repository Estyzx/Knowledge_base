/**
 * 通用折叠面板脚本
 * 支持种植技术库、病虫害库和土壤库
 */
$(document).ready(function() {
    console.log('Collapsible.js加载成功');
    
    // 初始化所有折叠面板
    function initCollapsible() {
        console.log('初始化折叠面板');
        
        // 设置初始状态
        $('.collapsible-section').each(function() {
            const $section = $(this);
            const $header = $section.find('.collapsible-header');
            const $body = $section.find('.collapsible-body');
            const $icon = $header.find('.toggle-icon');
            const isExpanded = $header.attr('aria-expanded') === 'true';
            
            // 确保内容可见性属性正确
            $body.css({
                'overflow': 'visible',
                'height': 'auto',
                'max-height': 'none'
            });
            
            // 应用展开或折叠状态
            if (isExpanded) {
                $header.addClass('expanded');
                $icon.css('transform', 'rotate(180deg)');
                $body.show();
            } else {
                $header.removeClass('expanded');
                $icon.css('transform', 'rotate(0deg)');
                $body.hide();
            }
        });
        
        // 防止重复绑定事件
        if(!window.collapsibleInitialized) {
            // 移除可能存在的事件处理器，防止重复绑定
            $('.collapsible-header').off('click.collapsible');
            
            // 绑定点击事件
            $('.collapsible-header').on('click.collapsible', function(e) {
                // 防止事件冒泡
                e.preventDefault();
                e.stopPropagation();
                
                const $header = $(this);
                const $body = $header.next('.collapsible-body');
                const $icon = $header.find('.toggle-icon');
                const isExpanded = $header.hasClass('expanded');
                
                // 切换展开状态
                if (isExpanded) {
                    $header.removeClass('expanded');
                    $icon.css('transform', 'rotate(0deg)');
                    $body.slideUp(300);
                    $header.attr('aria-expanded', 'false');
                } else {
                    $header.addClass('expanded');
                    $icon.css('transform', 'rotate(180deg)');
                    $body.slideDown(300);
                    $header.attr('aria-expanded', 'true');
                }
            });
            
            // 标记初始化完成
            window.collapsibleInitialized = true;
        }
        
        console.log('折叠面板初始化完成');
    }
    
    // 页面加载时初始化
    initCollapsible();
    
    // 确保在DOM完全加载后再次初始化
    $(window).on('load', function() {
        setTimeout(initCollapsible, 200);
    });
    
    // 暴露全局初始化方法，允许从其他脚本调用
    window.initializeCollapsiblePanels = initCollapsible;
});
