/**
 * 农业智库服务工作器
 * 用于缓存静态资源，提高页面加载速度
 */

// 缓存版本号
const CACHE_VERSION = 'v1';
const CACHE_NAME = `agricultural-knowledge-${CACHE_VERSION}`;

// 要缓存的静态资源 - 只包含本地资源，避免跨域问题
const STATIC_CACHE_URLS = [
  '/static/css/animations.css',
  '/static/css/progress-bar.css',
  '/static/js/app.js',
  '/static/js/progress-bar.js',
  '/static/js/performance.js',
  '/static/js/resource-optimizer.js',
  '/static/logo.svg',
];

// 安装事件 - 预缓存静态资源
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('缓存静态资源');
        // 使用Promise.all确保每个资源都独立处理
        return Promise.all(
          STATIC_CACHE_URLS.map(url => 
            fetch(url)
              .then(response => {
                if (!response.ok) {
                  throw new Error(`请求失败: ${url}`);
                }
                return cache.put(url, response);
              })
              .catch(error => {
                console.error(`缓存资源失败: ${url}`, error);
                // 继续处理其他资源
                return Promise.resolve();
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
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 拦截请求并从缓存中响应
self.addEventListener('fetch', event => {
  // 仅处理GET请求
  if (event.request.method !== 'GET') return;
  
  // 仅处理同源请求或安全的跨域请求
  const requestUrl = new URL(event.request.url);
  if (requestUrl.origin !== location.origin && 
      !STATIC_CACHE_URLS.some(url => event.request.url.includes(url))) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 返回缓存响应或网络请求
        return response || fetch(event.request)
          .then(fetchResponse => {
            // 不缓存非成功响应
            if (!fetchResponse || fetchResponse.status !== 200) {
              return fetchResponse;
            }
            
            // 缓存新响应
            const responseToCache = fetchResponse.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              })
              .catch(err => console.error('缓存更新失败:', err));
              
            return fetchResponse;
          });
      })
      .catch(() => {
        // 网络请求失败，可能离线
        // 可以返回自定义的离线页面
        return new Response('网络连接失败，请检查您的网络连接');
      })
  );
});

// 消息处理
self.addEventListener('message', event => {
  if (event.data && event.data.action === 'cache') {
    // 处理额外的缓存请求
    const urls = event.data.urls || [];
    caches.open(CACHE_NAME)
      .then(cache => {
        urls.forEach(url => {
          fetch(url)
            .then(response => {
              if (response.ok) cache.put(url, response);
            })
            .catch(err => console.error(`预缓存失败: ${url}`, err));
        });
      });
  }
});
