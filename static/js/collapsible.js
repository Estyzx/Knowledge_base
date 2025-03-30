document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有折叠面板
    initCollapsibleSections();
    
    // 保存折叠状态到本地存储
    function saveCollapseState(id, isExpanded) {
        if (typeof(Storage) !== "undefined") {
            localStorage.setItem('collapse_' + id, isExpanded ? 'expanded' : 'collapsed');
        }
    }
    
    // 从本地存储加载折叠状态
    function loadCollapseState(id) {
        if (typeof(Storage) !== "undefined") {
            return localStorage.getItem('collapse_' + id) === 'expanded';
        }
        return true; // 默认展开
    }
    
    // 初始化所有折叠面板
    function initCollapsibleSections() {
        const collapsibles = document.querySelectorAll('.collapsible-section');
        
        collapsibles.forEach(function(section) {
            const header = section.querySelector('.collapsible-header');
            const body = section.querySelector('.collapsible-body');
            const id = section.getAttribute('id');
            
            // 如果有本地存储的状态，应用它；如果没有，则默认展开
            const isExpanded = id ? loadCollapseState(id) : true;
            
            if (isExpanded) {
                body.classList.add('show');
                header.setAttribute('aria-expanded', 'true');
            } else {
                header.setAttribute('aria-expanded', 'false');
            }
            
            // 添加点击事件
            header.addEventListener('click', function() {
                const isExpanded = header.getAttribute('aria-expanded') === 'true';
                
                // 切换状态
                if (isExpanded) {
                    body.classList.remove('show');
                    header.setAttribute('aria-expanded', 'false');
                } else {
                    body.classList.add('show');
                    header.setAttribute('aria-expanded', 'true');
                }
                
                // 保存状态
                if (id) {
                    saveCollapseState(id, !isExpanded);
                }
            });
        });
    }
});