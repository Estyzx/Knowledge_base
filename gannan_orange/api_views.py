import json
from django.http import JsonResponse
from django.core.cache import cache
import requests

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
