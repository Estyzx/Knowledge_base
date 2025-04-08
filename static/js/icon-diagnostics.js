/**
 * Font Awesome 图标诊断工具
 * 用于检测图标显示问题并提供解决方案
 */

(function() {
    // 在页面加载完成后运行
    window.addEventListener('load', function() {
        console.log('运行图标诊断工具...');
        
        // 检查字体是否正确加载
        var fontLoaded = false;
        var testIcon = document.createElement('i');
        testIcon.className = 'fas fa-check';
        testIcon.style.display = 'none';
        document.body.appendChild(testIcon);
        
        if (window.getComputedStyle(testIcon, ':before').content !== 'none') {
            fontLoaded = true;
        }
        document.body.removeChild(testIcon);
        
        console.log('Font Awesome 字体加载状态:', fontLoaded ? '成功' : '失败');
        
        // 检查页面上的图标
        var totalIcons = 0;
        var missingIcons = 0;
        var iconTypes = {};
        
        document.querySelectorAll('.fas, .far, .fab').forEach(function(icon) {
            totalIcons++;
            
            // 获取图标类型
            var classes = Array.from(icon.classList);
            var iconClass = classes.find(cls => cls.startsWith('fa-'));
            if (iconClass) {
                iconTypes[iconClass] = (iconTypes[iconClass] || 0) + 1;
            }
            
            // 检查是否正确显示
            var computedStyle = window.getComputedStyle(icon, ':before');
            if (!computedStyle.content || computedStyle.content === 'none' || computedStyle.content === '') {
                missingIcons++;
                console.warn('缺失图标:', iconClass, icon);
            }
        });
        
        console.log('图标诊断结果:');
        console.log('- 总图标数量:', totalIcons);
        console.log('- 缺失图标数量:', missingIcons); 
        console.log('- 图标类型分布:', iconTypes);
        
        // 如果有超过10%的图标缺失，在控制台显示警告
        if (missingIcons > 0 && totalIcons > 0 && (missingIcons / totalIcons) > 0.1) {
            console.error('图标加载问题! 可能原因:');
            console.error('1. Font Awesome webfonts文件未正确加载');
            console.error('2. 使用了错误的图标名称或版本不兼容');
            console.error('3. CSS冲突导致图标样式被覆盖');
            console.error('建议解决方案:');
            console.error('- 检查/static/fontawesome/webfonts/目录是否包含所有字体文件');
            console.error('- 使用浏览器开发工具检查网络请求，看字体文件是否加载失败');
            console.error('- 考虑升级或降级到与代码兼容的Font Awesome版本(推荐5.15.4)');
        }
    });
})();
