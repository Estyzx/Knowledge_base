import time
import functools
from django.db import connection, reset_queries
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def query_debugger(func):
    """
    用于调试视图函数中的数据库查询
    使用方法: 在需要调试的视图函数上添加 @query_debugger 装饰器
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if settings.DEBUG:
            reset_queries()
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            query_count = len(connection.queries)
            query_time = sum(float(q.get('time', 0)) for q in connection.queries)
            
            logger.debug(f"视图函数: {func.__name__}")
            logger.debug(f"查询数量: {query_count}")
            logger.debug(f"查询耗时: {query_time:.3f}秒")
            logger.debug(f"总耗时: {end_time - start_time:.3f}秒")
            
            return result
        else:
            return func(*args, **kwargs)
    return wrapper

def cached_view(timeout=3600):
    """
    为视图函数结果添加缓存，减少重复计算和数据库查询
    使用方法: 在视图函数上添加 @cached_view(timeout=3600) 装饰器
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # 生成缓存键
            cache_key = f"view_cache_{func.__name__}_{request.path}"
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行视图函数
            result = func(request, *args, **kwargs)
            
            # 如果结果可缓存，存入缓存
            if hasattr(result, 'content'):
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def prefetch_related_objects(queryset, *relations):
    """
    使用预取关联对象减少数据库查询
    """
    if relations:
        return queryset.prefetch_related(*relations)
    return queryset
