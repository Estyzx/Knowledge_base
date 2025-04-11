from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """将字符串按指定分隔符分割成列表"""
    return value.split(arg)

@register.filter
def get_item(dictionary, key):
    """获取字典中的项目"""
    return dictionary.get(key)

@register.filter
def calculate_percentage(value, max_value):
    """计算百分比"""
    if max_value <= 0:
        return 0
    return int((value / max_value) * 100)

@register.filter(name='strip')
def strip(value):
    """去除字符串两端的空白字符"""
    return value.strip() if value else ""

@register.filter
def tag_list(tags_str, delimiter=','):
    """将标签字符串转换为标签列表"""
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(delimiter) if tag.strip()]
