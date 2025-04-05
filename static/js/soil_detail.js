(document).ready(function() {
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

    // 确保图标正确显示
    function ensureIconsVisible() {
        // 定义图标映射
        const iconDefs = {
            'soil-basic': '<i class="fas fa-info-circle"></i>',
            'soil-properties': '<i class="fas fa-microscope"></i>',
            'soil-suitable': '<i class="fas fa-seedling"></i>',
            'soil-management': '<i class="fas fa-tools"></i>',
            'soil-nutrition': '<i class="fas fa-flask"></i>'
        };
        
        // 为避免冲突，首先移除所有现有的点击事件
        $('.collapsible-header').off('click');
        
        // 设置所有图标
        Object.keys(iconDefs).forEach(id => {
            $(`#${id} .icon-container`).html(iconDefs[id]);
        });
        
        // 确保图标颜色为白色
        $('.icon-container i').css('color', 'white');
    }
    
    // 立即执行图标修复
    ensureIconsVisible();
    
    // 完全重写折叠面板实现以修复显示不完全问题 - 模仿病虫害详情页
    function initializeCollapsiblePanels() {
        // 首先移除所有已绑定的点击事件
        $('.collapsible-header').off('click');
        
        // 设置初始状态
        $('.collapsible-section').each(function() {
            const $header = $(this).find('.collapsible-header');
            const $body = $(this).find('.collapsible-body');
            const $icon = $header.find('.toggle-icon');
            const isExpanded = $header.attr('aria-expanded') === 'true';
            
            // 确保所有内容可以正常显示
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
        
        // 重新绑定点击事件 - 使用简化版本
        $('.collapsible-header').on('click', function() {
            const $header = $(this);
            const $body = $header.next('.collapsible-body');
            const $icon = $header.find('.toggle-icon');
            
            if ($header.hasClass('expanded')) {
                $header.removeClass('expanded');
                $icon.css('transform', 'rotate(0deg)');
                $body.slideUp(200);
            } else {
                $header.addClass('expanded');
                $icon.css('transform', 'rotate(180deg)');
                
                // 确保内容在显示前已经准备好完全展开
                $body.css({
                    'overflow': 'visible',
                    'height': 'auto',
                    'max-height': 'none'
                }).slideDown(200);
            }
        });
    }
    
    // 初始化折叠面板并确保在加载后再次运行
    initializeCollapsiblePanels();
    $(window).on('load', function() {
        setTimeout(initializeCollapsiblePanels, 200);
    });
    
    // 防止Bootstrap或其他库干扰折叠功能
    $(document).on('shown.bs.collapse hidden.bs.collapse', function() {
        setTimeout(initializeCollapsiblePanels, 200);
    });
    
    // 修复pH值指示器位置计算
    function calculatePhPosition() {
        $('.suitability-marker').each(function() {
            try {
                // 获取pH值
                const phValueStr = $(this).attr('data-ph-value') || 
                                  $(this).closest('.soil-property').find('.property-value').text();
                const phValue = parseFloat(phValueStr) || 7;
                
                // 将pH值(3-11)映射到百分比位置(0-100%)
                const position = ((phValue - 3) / 8) * 100;
                
                // 确保位置在有效范围内(0-100%)
                const clampedPosition = Math.max(0, Math.min(100, position));
                
                // 应用位置
                $(this).css('left', clampedPosition + '%');
                
                // 调试信息
                console.log(`pH值: ${phValue}, 位置: ${clampedPosition}%`);
            } catch (e) {
                console.error('设置pH值指示器位置时出错:', e);
                // 设置默认位置(中性pH 7)
                $(this).css('left', '50%');
            }
        });
    }
    
    // 页面加载后执行
    $(window).on('load', function() {
        // 延迟执行以确保DOM完全加载
        setTimeout(calculatePhPosition, 200);
    });
    
    // 立即执行一次
    calculatePhPosition();
    
    // 为土壤图片添加点击放大功能，类似病虫害页面
    $('.soil-image').on('click', function() {
        const src = $(this).attr('src');
        const alt = $(this).attr('alt');
        
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
        
        $('body').append($modal);
        const modal = new bootstrap.Modal($modal);
        modal.show();
        
        $modal.on('hidden.bs.modal', function() {
            $modal.remove();
        });
    });
    
    // 设置适宜度指示器位置
    $('.suitability-marker').each(function() {
        try {
            const value = $(this).data('value') || 50; // 默认居中
            $(this).css('left', value + '%');
        } catch (e) {
            console.error('Error setting marker position:', e);
            // 设置默认位置
            $(this).css('left', '50%');
        }
    });
    
    // 如果页面上有图表，初始化图表
    if (typeof Chart !== 'undefined' && $('#soilCompositionChart').length) {
        const ctx = document.getElementById('soilCompositionChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['沙粒', '淤泥', '粘土'],
                datasets: [{
                    data: [
                        parseFloat($('#sandContent').data('value') || 33),
                        parseFloat($('#siltContent').data('value') || 33),
                        parseFloat($('#clayContent').data('value') || 34)
                    ],
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 99, 132, 0.7)'
                    ],
                    borderColor: [
                        'rgba(255, 206, 86, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: '土壤成分构成'
                    }
                }
            }
        });
    }
    
    // 确保所有土壤数据正确显示
    function ensureSoilDataVisible() {
        // 检查土壤类型字段是否正确显示
        $('.property-value').each(function() {
            if ($(this).text().trim() === '') {
                $(this).text('未知');
            }
        });
        
        // 确保pH值指示器位置正确
        $('.suitability-marker').each(function() {
            try {
                // 获取pH值 - 使用data-ph-value属性
                const phValue = parseFloat($(this).attr('data-ph-value')) || 7;
                
                // 将pH值(3-11)映射到百分比位置(0-100%)
                const position = ((phValue - 3) / 8) * 100;
                
                // 确保位置在有效范围内(0-100%)
                const clampedPosition = Math.max(0, Math.min(100, position));
                
                // 应用位置
                $(this).css('left', clampedPosition + '%');
            } catch (e) {
                console.error('Error setting pH marker position:', e);
                // 设置默认位置(中性pH 7)
                $(this).css('left', '50%');
            }
        });
    }
    
    // 页面加载后执行
    $(window).on('load', function() {
        // 确保土壤数据显示
        ensureSoilDataVisible();
        
        // 初始化折叠面板并确保在加载后再次运行
        setTimeout(initializeCollapsiblePanels, 200);
    });
});
