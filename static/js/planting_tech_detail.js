$(document).ready(function() {
    /* 简化的滚动动画 - 优化性能 */
    function checkScrollFade() {
        $('.scroll-fade').each(function() {
            if ($(this).offset().top < ($(window).scrollTop() + $(window).height() - 100)) {
                $(this).addClass('visible');
            }
        });
    }
    
    // 初始检查和窗口滚动时的检查 - 使用节流函数减少调用频率
    checkScrollFade();
    var scrollThrottleTimer;
    $(window).on('scroll', function() {
        if (!scrollThrottleTimer) {
            scrollThrottleTimer = setTimeout(function() {
                // 返回顶部按钮可见性
                $('#backToTop').toggleClass('visible', $(window).scrollTop() > 300);
                
                // 仅在需要时执行滚动动画检查
                if ($('.scroll-fade:not(.visible)').length) {
                    checkScrollFade();
                }
                scrollThrottleTimer = null;
            }, 100);
        }
    });
    
    // 返回顶部按钮 - 使用平滑滚动
    $('#backToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 300);
        return false;
    });
    
    // 导航链接简化和性能优化
    $('.tech-nav-link').click(function(e) {
        e.preventDefault();
        var target = $($(this).attr('href'));
        $('html, body').animate({scrollTop: target.offset().top - 80}, 300);
        $('.tech-nav-link').removeClass('active');
        $(this).addClass('active');
    });
    
    // 删除确认
    $('#delete-btn').click(function(e) {
        e.preventDefault();
        var deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        deleteModal.show();
    });
    
    $('#confirmDelete').click(function() {
        $('#delete-form').submit();
    });

    // 简化版图标修复 - 只添加必要的图标
    const iconDefs = {
        'tech-basic-info': '<i class="fas fa-info-circle"></i>',
        'tech-description': '<i class="fas fa-file-signature"></i>',
        'tech-conditions': '<i class="fas fa-check-circle"></i>',
        'tech-steps': '<i class="fas fa-list-ol"></i>',
        'tech-notes': '<i class="fas fa-exclamation-triangle"></i>',
        'tech-equipment': '<i class="fas fa-tools"></i>',
        'tech-results': '<i class="fas fa-chart-line"></i>'
    };
    
    // 一次性设置所有图标
    Object.keys(iconDefs).forEach(id => {
        $(`#${id} .icon-container`).html(iconDefs[id]);
    });
    
    // 所有图标着色为白色
    $('.icon-container i').css('color', 'white');
    
    // 更高效的折叠面板实现
    $('.collapsible-header').on('click', function() {
        const $header = $(this);
        const $body = $header.next('.collapsible-body');
        const $icon = $header.find('.toggle-icon');
        const isExpanded = $header.hasClass('expanded');
        
        // 切换展开状态 - 使用简化的动画
        if (isExpanded) {
            $body.slideUp(200);
            $header.removeClass('expanded');
            $icon.css('transform', 'rotate(0deg)');
        } else {
            $body.slideDown(200);
            $header.addClass('expanded');
            $icon.css('transform', 'rotate(180deg)');
        }
    });
    
    // 初始化折叠面板状态 - 简化处理逻辑
    $('.collapsible-section').each(function() {
        const $header = $(this).find('.collapsible-header');
        const $body = $(this).find('.collapsible-body');
        
        if ($header.attr('aria-expanded') === 'true') {
            $body.show();
            $header.addClass('expanded');
            $header.find('.toggle-icon').css('transform', 'rotate(180deg)');
        } else {
            $body.hide();
        }
    });
});
