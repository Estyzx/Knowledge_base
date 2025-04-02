document.addEventListener('DOMContentLoaded', function() {
    if (typeof ClassicEditor !== 'undefined') {
        const editorContainer = document.querySelector('.rich-editor');
        if (!editorContainer) return;

        ClassicEditor
            .create(editorContainer, {
                language: 'zh-cn',
                height: '300px',
                toolbar: {
                    items: [
                        'undo', 'redo',
                        '|', 'heading',
                        '|', 'bold', 'italic',
                        '|', 'link', 'uploadImage', 'insertTable', 'mediaEmbed',
                        '|', 'bulletedList', 'numberedList',
                        '|', 'outdent', 'indent',
                        '|', 'blockQuote',
                        '|', 'sourceEditing'
                    ]
                },
                image: {
                    upload: {
                        types: ['jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']
                    }
                },
                simpleUpload: {
                    uploadUrl: '/upload/image/',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                }
            })
            .then(editor => {
                console.log('CKEditor initialized successfully');
            })
            .catch(error => {
                console.error('CKEditor initialization failed:', error);
            });
    }
});

// 获取CSRF Token的辅助函数
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}