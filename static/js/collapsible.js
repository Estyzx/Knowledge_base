document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有折叠面板
    initCollapsibleSections();
    
    // 错误处理函数
    function handleError(error, message) {
        console.error(message, error);
    }
    
    // 保存折叠状态到本地存储 - 添加错误处理
    function saveCollapseState(id, isExpanded) {
        try {
            if (typeof(Storage) !== "undefined") {
                localStorage.setItem('collapse_' + id, isExpanded ? 'expanded' : 'collapsed');
            }
        } catch (error) {
            handleError(error, '无法保存折叠状态');
        }
    }
    
    // 从本地存储加载折叠状态 - 添加错误处理
    function loadCollapseState(id) {
        try {
            if (typeof(Storage) !== "undefined") {
                return localStorage.getItem('collapse_' + id) === 'expanded';
            }
        } catch (error) {
            handleError(error, '无法加载折叠状态');
        }
        return true; // 默认展开
    }
    
    // 初始化所有折叠面板 - 优化性能和添加错误处理
    function initCollapsibleSections() {
        try {
            const collapsibles = document.querySelectorAll('.collapsible-section');
            if (!collapsibles.length) return;
            
            // 使用事件委托来减少事件监听器数量
            document.addEventListener('click', function(event) {
                const header = event.target.closest('.collapsible-header');
                if (!header) return;
                
                const section = header.closest('.collapsible-section');
                if (!section) return;
                
                const body = section.querySelector('.collapsible-body');
                if (!body) return;
                
                const id = section.getAttribute('id');
                const isExpanded = header.getAttribute('aria-expanded') === 'true';
                
                // 切换状态并添加平滑过渡
                if (isExpanded) {
                    body.style.maxHeight = '0';
                    setTimeout(() => {
                        body.classList.remove('show');
                        header.setAttribute('aria-expanded', 'false');
                    }, 200);
                } else {
                    body.classList.add('show');
                    header.setAttribute('aria-expanded', 'true');
                    body.style.maxHeight = body.scrollHeight + 'px';
                }
                
                // 保存状态
                if (id) {
                    saveCollapseState(id, !isExpanded);
                }
            });
            
            // 初始化每个折叠面板的初始状态
            collapsibles.forEach(function(section) {
                const header = section.querySelector('.collapsible-header');
                const body = section.querySelector('.collapsible-body');
                if (!header || !body) return;
                
                const id = section.getAttribute('id');
                
                // 如果有本地存储的状态，应用它；如果没有，则默认展开
                const isExpanded = id ? loadCollapseState(id) : true;
                
                if (isExpanded) {
                    body.classList.add('show');
                    header.setAttribute('aria-expanded', 'true');
                    body.style.maxHeight = body.scrollHeight + 'px';
                } else {
                    header.setAttribute('aria-expanded', 'false');
                    body.style.maxHeight = '0';
                }
            });
        } catch (error) {
            handleError(error, '初始化折叠面板失败');
        }
    }
});