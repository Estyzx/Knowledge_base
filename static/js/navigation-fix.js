/**
 * 导航修复脚本 - 解决浏览器后退按钮问题
 */
(function() {
    // 保存当前时间戳到会话存储，用于检测后退操作
    function savePageState() {
        const timestamp = new Date().getTime();
        const currentPath = window.location.pathname;
        sessionStorage.setItem('lastPage', currentPath);
        sessionStorage.setItem('lastPageTimestamp', timestamp);
    }

    // 页面加载时检查是否是后退操作
    function checkBackNavigation() {
        const currentPath = window.location.pathname;
        const lastPage = sessionStorage.getItem('lastPage');
        const timestamp = sessionStorage.getItem('lastPageTimestamp');
        
        // 如果是从后退按钮回到的页面
        if (window.performance && window.performance.navigation.type === 2) {
            // 强制刷新页面，确保内容正确加载
            window.location.reload();
            return;
        }
        
        // 保存当前页面状态
        savePageState();
    }

    // 处理pageshow事件，这个事件在页面从缓存中恢复时会触发
    function handlePageShow(event) {
        // 如果页面是从缓存加载的(例如后退按钮)
        if (event.persisted) {
            // 强制刷新页面，确保内容正确显示
            window.location.reload();
        }
    }

    // 监听页面可见性变化
    function handleVisibilityChange() {
        if (document.visibilityState === 'visible') {
            // 从隐藏状态变为可见状态，可能是切换回此标签页
            // 检查页面内容是否完整，如果不完整则刷新
            if (document.body.classList.contains('content-loading') || 
                document.querySelectorAll('.placeholder').length > 0) {
                window.location.reload();
            }
        }
    }

    // 初始化导航修复
    function initNavigationFix() {
        // 监听页面显示事件（处理从缓存加载的情况）
        window.addEventListener('pageshow', handlePageShow);
        
        // 监听页面可见性变化（处理标签页切换）
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // 页面加载完成后检查是否是后退导航
        document.addEventListener('DOMContentLoaded', checkBackNavigation);
        
        // 向页面添加标记，表示内容正在加载
        document.body.classList.add('content-loading');
        
        // 在DOM内容加载完成后移除加载标记
        window.addEventListener('load', function() {
            document.body.classList.remove('content-loading');
        });
    }

    // 执行初始化
    initNavigationFix();
})();
