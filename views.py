// ...existing code...

def soil_type_detail(request, soil_id):
    """土壤类型详情页"""
    try:
        soil = SoilType.objects.get(id=soil_id)
    except SoilType.DoesNotExist:
        return redirect('orange:soil_list')
        
    # 确保模板上下文中包含必要的数据
    context = {
        'soil': soil,
        'referer': request.META.get('HTTP_REFERER', reverse('orange:soil_list'))
    }
    
    # 为调试添加额外数据
    context['debug_info'] = {
        'has_type': hasattr(soil, 'type'),
        'type_value': getattr(soil, 'type', 'unknown'),
        'get_type_display': soil.get_type_display(),
    }
    
    return render(request, 'gannan_orange/soil_type_detail.html', context)

// ...existing code...