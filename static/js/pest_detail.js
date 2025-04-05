$(document).ready(function() {
    /* 滚动动画 */
    function checkScrollFade() {
        $('.scroll-fade').each(function() {
            if ($(this).offset().top < ($(window).scrollTop() + $(window).height() - 100)) {
                $(this).addClass('visible');
            }
        });
    }
    
    // 初始检查和窗口滚动时的检查
    checkScrollFade();
    $(window).on('scroll', function() {
        // 返回顶部按钮可见性
        $('#backToTop').toggleClass('visible', $(this).scrollTop() > 300);
        
        // 仅在需要时执行滚动动画检查
        if ($('.scroll-fade:not(.visible)').length) {
            checkScrollFade();
        }
    });
    
    // 返回顶部按钮
    $('#backToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 600);
        return false;
    });
    
    // 导航链接
    $('.nav-link').click(function(e) {
        e.preventDefault();
        var target = $($(this).attr('href'));
        $('html, body').animate({scrollTop: target.offset().top - 80}, 600);
        $('.nav-link').removeClass('active');
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

    // 改进图标设置以确保所有图标都能正确显示
    function ensureIconsVisible() {
        // 定义图标映射
        const iconDefs = {
            'pest-info': '<i class="fas fa-bug"></i>',
            'pest-symptoms': '<i class="fas fa-clipboard-list"></i>',
            'pest-lifecycle': '<i class="fas fa-redo-alt"></i>',
            'pest-treatment': '<i class="fas fa-prescription-bottle-alt"></i>',
            'pest-prevention': '<i class="fas fa-shield-alt"></i>'
        };
        
        // 先检查图标是否已经存在并可见
        let needFix = false;
        Object.keys(iconDefs).forEach(id => {
            const $icon = $(`#${id} .icon-container i`);
            if ($icon.length === 0 || $icon.width() === 0) {
                needFix = true;
                return false; // 跳出循环
            }
        });
        
        // 如果需要修复图标
        if (needFix) {
            // 设置所有图标
            Object.keys(iconDefs).forEach(id => {
                $(`#${id} .icon-container`).html(iconDefs[id]);
            });
            
            // 确保图标颜色为白色
            $('.icon-container i').css('color', 'white');
        }
    }
    
    // 页面加载后立即执行，并在一小段延迟后再次执行以处理可能的延迟加载
    ensureIconsVisible();
    setTimeout(ensureIconsVisible, 500);
    
    // 折叠面板实现
    $('.collapsible-header').on('click', function() {
        const $header = $(this);
        const $body = $header.next('.collapsible-body');
        const $icon = $header.find('.toggle-icon');
        const isExpanded = $header.hasClass('expanded');
        
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
    
    // 改进初始化折叠面板状态的代码以确保正确显示
    $('.collapsible-section').each(function() {
        const $header = $(this).find('.collapsible-header');
        const $body = $(this).find('.collapsible-body');
        const isExpanded = $header.attr('aria-expanded') === 'true';
        
        if (isExpanded) {
            $body.show();
            $header.addClass('expanded');
            $header.find('.toggle-icon').css('transform', 'rotate(180deg)');
        } else {
            $body.hide();
            $header.removeClass('expanded');
            $header.find('.toggle-icon').css('transform', 'rotate(0deg)');
        }
    });
    
    // 为图片添加可点击放大预览功能
    $('.pest-image').on('click', function() {
        const src = $(this).attr('src');
        const alt = $(this).attr('alt');
        
        // 创建一个临时模态框显示大图
        const $modal = $(`
            <div class="modal fade" id="imageModal" tabindex="-1">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${alt}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-0">
                            <img src="${src}" class="img-fluid w-100" alt="${alt}">
                        </div>
                    </div>
                </div>
            </div>
        `);
        
        // 添加到文档并显示
        $('body').append($modal);
        const modal = new bootstrap.Modal($modal);
        modal.show();
        
        // 模态框关闭后删除它
        $modal.on('hidden.bs.modal', function() {
            $modal.remove();
        });
    });
});
