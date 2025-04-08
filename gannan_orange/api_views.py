import json
from django.http import JsonResponse
from django.core.cache import cache
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone

def weather_api(request):
    """API端点，返回缓存的天气数据或实时获取新数据"""
    weather_data = cache.get('weather_data')
    current_weather = cache.get('current_weather')
    
    # 如果缓存为空，获取新数据
    if not weather_data or not current_weather:
        try:
            # 获取天气预报数据
            url = "https://api.seniverse.com/v3/weather/daily.json?key=SsIcJ_YpHt1dJPr1Q&location=ganzhou&language=zh-Hans&unit=c&start=0&days=5"
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                
                # 处理天气数据
                update_data = data['results'][0]['last_update'][:10]
                humidity = data['results'][0]['daily'][0]['humidity']
                wind_speed = data['results'][0]['daily'][0]['wind_speed']
                code_day = data['results'][0]['daily'][0]['code_day']
                
                # 存入缓存
                weather_data = {
                    'update_data': update_data,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'code_day': code_day,
                    'days': data['results'][0]['daily'],
                }
                
                # 获取实时天气数据
                url1 = "https://api.seniverse.com/v3/weather/now.json?key=SsIcJ_YpHt1dJPr1Q&location=ganzhou&language=zh-Hans&unit=c"
                response1 = requests.get(url1, timeout=3)
                
                if response1.status_code == 200:
                    data1 = response1.json()
                    current_weather = {
                        'temperature': data1['results'][0]['now']['temperature'],
                        'text': data1['results'][0]['now']['text'],
                    }
                    
                    # 缓存3小时
                    cache.set('weather_data', weather_data, 60*60*3)
                    cache.set('current_weather', current_weather, 60*60*3)
        except Exception as e:
            # 出错时返回默认数据
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'weather_data': {
                    'update_data': '数据获取失败',
                    'humidity': 'N/A',
                    'wind_speed': 'N/A',
                    'code_day': '99',
                    'days': []
                },
                'current_weather': {
                    'temperature': '--',
                    'text': '数据获取中'
                }
            })
    
    # 返回JSON数据
    return JsonResponse({
        'status': 'success',
        'weather_data': weather_data,
        'current_weather': current_weather
    })

@login_required
def review_history_api(request, content_type, content_id):
    """
    获取指定内容的审核历史记录
    """
    # 检查用户权限
    if not (request.user.is_staff or getattr(request.user, 'is_expert', False)):
        return JsonResponse({
            'success': False,
            'message': '您没有查看审核历史的权限'
        }, status=403)
    
    # 获取审核历史记录
    history = ReviewHistory.objects.filter(
        content_type=content_type,
        content_id=content_id
    ).order_by('-review_date')
    
    # 获取对应的内容对象
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
    
    # 转换为JSON格式
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
        
        # 尝试获取内容名称
        try:
            if hasattr(item, 'content_name'):
                data['content_name'] = item.content_name
            elif content_object and hasattr(content_object, 'name'):
                data['temp_content_name'] = content_object.name
        except:
            pass
            
        history_data.append(data)
    
    return JsonResponse({
        'success': True,
        'history': history_data
    })

@login_required
@require_POST
def quick_review_api(request, content_type, content_id):
    """
    快速审核API
    """
    # 检查用户权限
    if not (request.user.is_staff or getattr(request.user, 'is_expert', False)):
        return JsonResponse({
            'success': False,
            'message': '您没有审核权限'
        }, status=403)
    
    # 解析请求数据
    try:
        data = json.loads(request.body)
        action = data.get('action')
        comment = data.get('comment', '')
        
        # 验证操作
        if action not in ['approve', 'reject']:
            return JsonResponse({
                'success': False,
                'message': '无效的审核操作'
            }, status=400)
        
        # 如果是拒绝操作但没有填写审核意见
        if action == 'reject' and not comment:
            return JsonResponse({
                'success': False,
                'message': '拒绝操作必须填写审核意见'
            }, status=400)
        
        # 根据内容类型获取对应的模型
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
        
        # 获取对象
        Model = model_map[content_type]
        obj = get_object_or_404(Model, id=content_id)
        
        # 更新审核状态
        obj.review_status = 'approved' if action == 'approve' else 'rejected'
        obj.reviewer = request.user
        obj.review_comment = comment
        obj.review_date = timezone.now()
        obj.save()
        
        # 创建审核历史记录
        ReviewHistory.objects.create(
            content_type=content_type,
            content_id=obj.id,
            reviewer=request.user,
            action=action,
            comment=comment,
            content_name=obj.name  # 添加内容名称
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
