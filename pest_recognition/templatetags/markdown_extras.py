import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def markdown_to_html(text):
    """将Markdown文本转换为HTML"""
    # 配置扩展，使其支持表格、代码高亮等
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
    ]
    
    # 转换Markdown为HTML
    html = markdown.markdown(text, extensions=extensions)
    
    # 标记为安全输出，避免HTML被转义
    return mark_safe(html)
