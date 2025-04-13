import json
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .views import HomePage

def weather_api(request):
    """API端点，返回天气数据（缓存优先）"""
    # 使用缓存提高性能
    weather_data = cache.get('weather_data')
    current_weather = cache.get('current_weather')
    
    if not weather_data or not current_weather:
        try:
            # 复用HomePage中的天气获取逻辑
            home_page = HomePage()
            weather_result = home_page.fetch_weather_data()
            
            if weather_result:
                weather_data, current_weather = weather_result
                # 3小时缓存
                cache.set('weather_data', weather_data, 60*60*3)
                cache.set('current_weather', current_weather, 60*60*3)
            else:
                # 错误响应
                return JsonResponse({
                    'status': 'error',
                    'message': '天气API响应错误',
                    'weather_data': {'update_data': '数据获取失败', 'humidity': 'N/A', 'wind_speed': 'N/A', 'code_day': '99', 'days': []},
                    'current_weather': {'temperature': '--', 'text': '数据获取中'},
                })
        except Exception as e:
            # 异常响应带默认数据
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'weather_data': {'update_data': '数据获取失败', 'humidity': 'N/A', 'wind_speed': 'N/A', 'code_day': '99', 'days': []},
                'current_weather': {'temperature': '--', 'text': '数据获取中'},
            })
    
    # 成功响应
    return JsonResponse({
        'status': 'success',
        'weather_data': weather_data,
        'current_weather': current_weather
    })

@login_required
def review_history_api(request, content_type, content_id):
    """获取指定内容的审核历史记录"""
    # 审核权限验证
    if not (request.user.is_staff or getattr(request.user, 'is_expert', False)):
        return JsonResponse({
            'success': False,
            'message': '您没有查看审核历史的权限'
        }, status=403)
    
    # 获取审核历史
    history = ReviewHistory.objects.filter(
        content_type=content_type,
        content_id=content_id
    ).order_by('-review_date')
    
    # 获取相关内容对象
    content_object = None
    model_map = {
        'variety': Variety,
        'planting_tech': PlantingTech,
        'pest': Pest,
        'soil_type': SoilType,
    }
    
    if content_type in model_map:
        Model = model_map[content_type]
        try:
            content_object = Model.objects.get(id=content_id)
        except Model.DoesNotExist:
            content_object = None
    
    # 转换为JSON
    history_data = []
    for item in history:
        data = {
            'id': item.id,
            'reviewer': item.reviewer.username,
            'action': item.action,
            'comment': item.comment,
            'review_date': item.review_date.strftime('%Y-%m-%d %H:%M:%S'),
            'content_id': item.content_id
        }
        
        # 处理内容名称
        if hasattr(item, 'content_name') and item.content_name:
            data['content_name'] = item.content_name
        elif content_object and hasattr(content_object, 'name'):
            data['temp_content_name'] = content_object.name
            
        history_data.append(data)
    
    return JsonResponse({
        'success': True,
        'history': history_data
    })

@login_required
@require_POST
def quick_review_api(request, content_type, content_id):
    """快速审核内容的API端点"""
    # 权限检查
    if not (request.user.is_staff or getattr(request.user, 'is_expert', False)):
        return JsonResponse({
            'success': False,
            'message': '您没有审核权限'
        }, status=403)
    
    try:
        # 解析请求数据
        data = json.loads(request.body)
        action = data.get('action')
        comment = data.get('comment', '')
        
        # 验证操作类型
        if action not in ['approve', 'reject']:
            return JsonResponse({
                'success': False,
                'message': '无效的审核操作'
            }, status=400)
        
        # 拒绝需要提供理由
        if action == 'reject' and not comment:
            return JsonResponse({
                'success': False,
                'message': '拒绝操作必须填写审核意见'
            }, status=400)
        
        # 模型映射
        model_map = {
            'variety': Variety,
            'planting_tech': PlantingTech,
            'pest': Pest,
            'soil_type': SoilType
        }
        
        if content_type not in model_map:
            return JsonResponse({
                'success': False,
                'message': '无效的内容类型'
            }, status=400)
        
        # 获取对象并更新
        Model = model_map[content_type]
        obj = get_object_or_404(Model, id=content_id)
        
        obj.review_status = 'approved' if action == 'approve' else 'rejected'
        obj.reviewer = request.user
        obj.review_comment = comment
        obj.review_date = timezone.now()
        obj.save()
        
        # 创建审核历史
        ReviewHistory.objects.create(
            content_type=content_type,
            content_id=obj.id,
            reviewer=request.user,
            action=action,
            comment=comment,
            content_name=obj.name
        )
        
        return JsonResponse({
            'success': True,
            'message': f"{'审核通过' if action == 'approve' else '审核拒绝'}成功"
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '无效的请求数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
