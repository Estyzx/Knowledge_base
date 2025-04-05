from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """将value乘以arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
    
@register.filter
def ph_to_position(value):
    """将pH值(3-11)转换为百分比位置(0-100%)"""
    try:
        ph = float(value)
        # 确保pH值在3-11范围内
        ph = max(3, min(11, ph))
        # 计算位置百分比
        position = ((ph - 3) / 8) * 100
        return position
    except (ValueError, TypeError):
        # 默认返回中性pH值(7)对应的位置
        return 50
