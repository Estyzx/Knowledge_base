/**
 * 农业智库服务工作器
 * 修复缓存问题和错误处理
 */

// 缓存版本号和名称
const CACHE_VERSION = 'v2';
const CACHE_NAME = `agri-knowledge-${CACHE_VERSION}`;

// 要缓存的重要静态资源 - 减少数量，只保留核心资源
const STATIC_CACHE_URLS = [
  '/static/logo.svg',
  '/static/css/animations.css',
  '/static/js/app.js'
];

// 安装事件 - 使用更健壮的缓存方法
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('正在预缓存核心资源');
        
        // 单独处理每个资源请求，忽略失败的请求
        return Promise.allSettled(
          STATIC_CACHE_URLS.map(url => 
            fetch(url, { cache: 'no-cache' })
              .then(response => {
                if (response && response.ok) {
                  return cache.put(url, response);
                }
                console.warn(`无法缓存: ${url}, 状态: ${response ? response.status : '未知'}`);
                return Promise.resolve();
              })
              .catch(error => {
                console.error(`预缓存失败: ${url}`, error.message);
                return Promise.resolve(); // 继续处理其他资源
              })
          )
        );
      })
      .then(() => self.skipWaiting())
  );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => cacheName.startsWith('agri-knowledge-') && cacheName !== CACHE_NAME)
            .map(cacheName => {
              console.log('删除旧缓存:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('服务工作器已激活');
        return self.clients.claim();
      })
  );
});

// 拦截请求 - 使用网络优先策略，降级到缓存
self.addEventListener('fetch', event => {
  // 仅处理GET请求和同源请求
  if (event.request.method !== 'GET' || 
      new URL(event.request.url).origin !== self.location.origin) {
    return;
  }
  
  // 仅缓存静态资源路径
  if (!event.request.url.includes('/static/')) {
    return;
  }

  event.respondWith(
    // 网络优先策略
    fetch(event.request)
      .then(response => {
        // 请求成功 - 克隆响应并更新缓存
        if (response && response.ok) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => cache.put(event.request, responseToCache))
            .catch(err => console.warn('缓存更新失败:', err.message));
        }
        return response;
      })
      .catch(() => {
        // 网络失败 - 尝试从缓存获取
        return caches.match(event.request)
          .then(cachedResponse => {
            if (cachedResponse) {
              console.log('从缓存提供:', event.request.url);
              return cachedResponse;
            }
            // 没有缓存，返回简单的离线响应
            if (event.request.headers.get('accept').includes('text/html')) {
              return new Response('您当前处于离线状态，请检查网络连接。', {
                headers: { 'Content-Type': 'text/html; charset=utf-8' }
              });
            }
            return new Response('离线资源不可用');
          });
      })
  );
});

// 消息处理
self.addEventListener('message', event => {
  if (event.data && event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});

// 添加一个离线页面缓存
self.addEventListener('message', event => {
  if (event.data && event.data.action === 'cacheHomePage') {
    caches.open(CACHE_NAME)
      .then(cache => {
        return fetch('/')
          .then(response => {
            if (response.ok) {
              return cache.put('/', response);
            }
          })
          .catch(err => console.warn('首页缓存失败:', err.message));
      });
  }
});
