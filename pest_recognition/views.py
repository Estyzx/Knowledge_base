import os
import random
import re
import requests
import time
import logging
import base64
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.contrib import messages

from .models import MODEL_SELECTION_GUIDE, RecognitionHistory, API_CONFIG
from gannan_orange.models import Pest

# 配置日志
logger = logging.getLogger(__name__)

def recognize_image(image_file, selected_model=None):
    """
    通过通义千问视觉模型识别图像中的病虫害
    
    Args:
        image_file: 上传的图像文件
        selected_model: 可选指定使用的模型名称
    """
    # 检查API是否已配置
    if not API_CONFIG.get('enabled', False):
        return _mock_recognition()
    
    # 使用指定模型或默认模型
    model = selected_model or API_CONFIG.get('model', 'qwen2.5-vl-72b-instruct')
    
    try:
        # 简单地读取图像数据
        image_file.seek(0)  # 确保从文件开头读取
        image_data = image_file.read()
        
        # 直接将整个图像编码为base64
        img_str = base64.b64encode(image_data).decode('utf-8')
        
        # 准备API请求数据 - 针对通义千问模型优化
        api_url = API_CONFIG['api_url']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_CONFIG["api_key"]}'
        }
        
        # 通义千问模型请求格式
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一位专业的农业病虫害识别专家，请识别图片中的植物病虫害。给出名称、类型和防治建议。'},
                {'role': 'user', 'content': [
                    {'type': 'text', 'text': '请识别这张图片中植物的病虫害情况，并告诉我它的名称、危害程度、特征和防治方法。'},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img_str}'}}
                ]}
            ],
            'temperature': 0.2,  # 降低随机性，提高准确性
            'max_tokens': 800,
        }
        
        # 发送API请求
        start_time = time.time()
        response = requests.post(
            api_url, 
            headers=headers,
            json=payload,
            timeout=API_CONFIG['timeout']
        )
        response_time = time.time() - start_time
        logger.info(f"API响应时间: {response_time:.2f}秒，使用模型: {model}")
        
        # 处理API响应
        if response.status_code == 200:
            result = response.json()
            api_response = result
            
            # 记录原始响应，便于调试
            logger.debug(f"API原始响应: {result}")
            
            # 从通义千问的响应中提取信息
            try:
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # 格式化内容，确保Markdown格式正确
                formatted_content = content
                
                # 添加标题标记，如果没有的话
                if not content.strip().startswith('#'):
                    formatted_content = f"# 病虫害识别结果\n\n{formatted_content}"
                
                # 将常见的段落格式化为Markdown
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)病害名称', '\n\n## 病害名称', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)虫害名称', '\n\n## 虫害名称', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)名称', '\n\n## 名称', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)特征', '\n\n## 特征', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)症状', '\n\n## 症状', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)防治方法', '\n\n## 防治方法', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)防治建议', '\n\n## 防治建议', formatted_content)
                formatted_content = re.sub(r'(?<!\n)\n(?!\n)危害程度', '\n\n## 危害程度', formatted_content)
                
                # 将连续的数字+点开头的行转换为有序列表
                formatted_content = re.sub(r'(?<!\n)\n(\d+)[\.、]', r'\n\n\1.', formatted_content)
                
                # 将连续的短横线或星号开头的行转换为无序列表
                formatted_content = re.sub(r'(?<!\n)\n[-*]', r'\n\n-', formatted_content)
                
                # 增强型病虫害名称提取，适用于复杂的AI返回结果
                pest_name = None
                confidence = 0.0
                multiple_diseases = []  # 用于存储识别到的多种可能病害
                
                # 1. 首先检查是否包含明确的"名称"标签
                name_patterns = [
                    # 常规名称形式
                    r'名称[：:]\s*([^\n\r]+)',
                    r'病害名称[：:]\s*([^\n\r]+)',
                    r'虫害名称[：:]\s*([^\n\r]+)',
                    r'中文名[：:]\s*([^\n\r]+)',  # 添加中文名匹配
                    r'学名[：:]\s*([^\n\r]+)',    # 添加学名匹配
                    # 通义千问常用的格式
                    r'\*\*名称\*\*：\s*([^\n\r]+)',
                    r'\*\*病害名称\*\*：\s*([^\n\r]+)',
                    r'\*\*虫害名称\*\*：\s*([^\n\r]+)',
                    r'\*\*中文名\*\*：\s*([^\n\r]+)',
                    r'\*\*学名\*\*：\s*([^\n\r]+)',
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, content)
                    if match:
                        pest_name = match.group(1).strip()
                        # 清理掉可能的markdown标记或括号内容
                        pest_name = re.sub(r'[（\(].+?[）\)]', '', pest_name)
                        pest_name = re.sub(r'\*\*|\*', '', pest_name)
                        confidence = 0.85  # 当找到明确的名称标签时，给予较高的0.85基础置信度
                        break
                
                # 2. 其次检查可能的病害标题
                if not pest_name:
                    title_patterns = [
                        r'###\s*(.+?病[毒菌])',  # 匹配 ### xxx病毒/病菌
                        r'####\s*\d+\.\s*病害：\s*(.+?)[（\(\n\r]',  # 匹配 #### 1. 病害：xxx（
                        r'病害[识诊]?[别断]?结果[：:]\s*(.+?)[（\(\n\r]',  # 病害识别结果：xxx
                    ]
                    
                    for pattern in title_patterns:
                        match = re.search(pattern, content)
                        if match:
                            pest_name = match.group(1).strip()
                            pest_name = re.sub(r'\*\*|\*', '', pest_name)
                            confidence = 0.82  # 从标题中提取病害名称时，给予0.82基础置信度
                            break
                
                # 3. 处理简短响应
                if not pest_name and len(content) < 200:
                    # 针对简短响应的直接匹配
                    first_sentence = content.split('。')[0] if '。' in content else content
                    disease_patterns = [
                        r'是([^，。]+?(?:病|虫害))',  # "这种病害是小麦锈病"
                        r'为([^，。]+?(?:病|虫害))',  # "这种疾病为小麦锈病"
                        r'诊断(?:为|是)([^，。]+?(?:病|虫害))',  # "诊断为小麦锈病"
                        r'确认(?:为|是)([^，。]+?(?:病|虫害))',  # "确认是小麦锈病"
                        r'属于([^，。]+?(?:病|虫害))'  # "属于条纹花叶病"
                    ]
                    
                    for pattern in disease_patterns:
                        match = re.search(pattern, first_sentence)
                        if match:
                            direct_pest_name = match.group(1).strip()
                            # 直接匹配数据库
                            common_pests = list(Pest.objects.values('id', 'name'))
                            for pest_obj in common_pests:
                                if direct_pest_name in pest_obj['name'] or pest_obj['name'] in direct_pest_name:
                                    pest_name = pest_obj['name']
                                    confidence = 0.85  # 简短响应直接匹配数据库成功时，给予高置信度0.85
                                    logger.info(f"简短响应直接匹配成功: '{direct_pest_name}' -> '{pest_name}'")
                                    break
                            
                            # 如果没有直接匹配到数据库，也使用检测到的名称
                            if not pest_name:
                                pest_name = direct_pest_name
                                confidence = 0.75  # 给予较低的置信度0.75
                            break
                
                # 4. 使用模糊匹配在数据库中匹配现有病害
                if not pest_name:
                    common_pests = list(Pest.objects.values('id', 'name'))
                    
                    # 预处理文本：分段并清理
                    paragraphs = re.split(r'\n\n+', content)
                    cleaned_paragraphs = []
                    for para in paragraphs:
                        # 移除标点符号和特殊字符，便于模糊匹配
                        clean_para = re.sub(r'[^\w\s]', '', para)
                        cleaned_paragraphs.append((para, clean_para))
                    
                    # 模糊匹配逻辑
                    best_match = None
                    best_match_score = 0
                    best_match_pest = None
                    
                    for pest_obj in common_pests:
                        pest_name_clean = re.sub(r'[^\w\s]', '', pest_obj['name'])
                        
                        # 1. 尝试直接匹配完整名称
                        for para, clean_para in cleaned_paragraphs:
                            if pest_obj['name'] in para:
                                # 计算上下文相关性得分
                                context_score = _calculate_context_score(para, pest_obj['name'])
                                if context_score > best_match_score:
                                    best_match = pest_obj['name']
                                    best_match_score = context_score
                                    best_match_pest = pest_obj
                        
                        # 2. 尝试匹配没有标点的名称
                        if not best_match:
                            for para, clean_para in cleaned_paragraphs:
                                if pest_name_clean in clean_para:
                                    context_score = _calculate_context_score(para, pest_obj['name'])
                                    if context_score > best_match_score:
                                        best_match = pest_obj['name']
                                        best_match_score = context_score
                                        best_match_pest = pest_obj
                        
                        # 3. 尝试部分匹配 - 适用于长名称的部分匹配
                        if not best_match and len(pest_name_clean) > 4:
                            name_parts = pest_name_clean.split()
                            for part in name_parts:
                                if len(part) < 2:  # 跳过太短的词
                                    continue
                                for para, clean_para in cleaned_paragraphs:
                                    if part in clean_para:
                                        # 计算匹配度分数
                                        match_score = 0.5 + (0.05 * len(part))  # 较长的词给更高分数
                                        if match_score > best_match_score:
                                            best_match = pest_obj['name']
                                            best_match_score = match_score
                                            best_match_pest = pest_obj
                    
                    # 如果找到合适的匹配，设置结果
                    if best_match_pest and best_match_score >= 0.6:
                        pest_name = best_match
                        confidence = best_match_score  # 置信度等于上下文相关性得分
                        
                        # 记录匹配细节（调试用）
                        logger.debug(f"模糊匹配成功: {pest_name}, 置信度: {confidence:.2f}")
                
                # 5. 检查是否包含"烟草花叶病毒"和"TMV"这样的格式（特殊处理）
                if not pest_name:
                    special_pattern = r'([^，。\n\r]{2,15}?(?:病毒|病菌|病害|虫害))\s*(?:\(([A-Z\s]+)\))?'
                    matches = re.finditer(special_pattern, content)
                    for match in matches:
                        potential_name = match.group(1).strip()
                        if len(potential_name) > 1:  # 确保名称不是太短
                            pest_name = potential_name
                            confidence = 0.75  # 给予中等置信度0.75
                            break
                
                # 6. 识别多病虫害情况
                multiple_diseases = []
                if '可能的病虫害' in content or'病虫害：' in content:
                    # 提取所有可能的病害名称
                    pattern = r'(?:\d+\.\s*病害：|####\s*\d+\.\s*病害：|\*\*名称\*\*：)\s*([^\n\r（\(]+)'
                    disease_matches = re.finditer(pattern, content)
                    for match in disease_matches:
                        disease = match.group(1).strip()
                        disease = re.sub(r'\*\*|\*', '', disease)
                        if disease and len(disease) > 1:
                            multiple_diseases.append({
                                'name': disease,
                                'type': '病害'
                            })
                            
                    # 提取所有可能的虫害名称
                    pattern = r'(?:\d+\.\s*虫害：|####\s*\d+\.\s*虫害：|\*\*名称\*\*：)\s*([^\n\r（\(]+)'
                    pest_matches = re.finditer(pattern, content)
                    for match in pest_matches:
                        pest = match.group(1).strip()
                        pest = re.sub(r'\*\*|\*', '', pest)
                        if pest and len(pest) > 1:
                            multiple_diseases.append({
                                'name': pest,
                                'type': '虫害'
                            })
                
                # 如果识别到多个病虫害，选择第一个作为主要结果
                if multiple_diseases and not pest_name:
                    pest_name = multiple_diseases[0]['name']
                    confidence = 0.80  # 给予较高置信度0.80
                    
                # 7. 最后的备用方案：使用关键词提取
                if not pest_name and len(content) < 300:
                    # 先移除一些常见的描述词和连词
                    simplified_text = re.sub(r'这种|属于|是|为|主要|一种|可能|疑似|建议|防治|方法|包括', '', content)
                    # 查找内容中包含"病"或"虫"的词语
                    disease_terms = re.findall(r'[\w]{1,10}[病虫害][\w]{0,5}', simplified_text)
                    if disease_terms:
                        pest_name = disease_terms[0]
                        confidence = 0.65  # 给予较低置信度0.65
                        logger.info(f"从简短内容中提取潜在病名: {pest_name}")
                
                # 如果找到了病虫害名称，则尝试匹配到数据库中的记录
                if pest_name and confidence > 0.5:
                    # 高级名称匹配策略
                    matching_pests = []
                    
                    # 1. 首先尝试精确匹配
                    exact_matches = Pest.objects.filter(name__iexact=pest_name)
                    if exact_matches.exists():
                        # 记录找到了精确匹配
                        logger.info(f"精确匹配成功: {pest_name}")
                        # 在API响应中添加识别信息
                        api_response['extracted_info'] = {
                            'pest_name': pest_name,
                            'confidence': confidence,
                            'full_response': content,
                            'markdown_response': formatted_content,
                            'multiple_diseases': multiple_diseases if multiple_diseases else None
                        }
                        return exact_matches.first(), confidence, api_response, model, response_time
                    
                    # 2. 处理常见的病虫害名称变体情况
                    cleaned_pest_name = pest_name.replace('病害', '').replace('虫害', '').strip()
                    
                    # 特殊处理识别结果中包含多个词的情况
                    # 例如"小麦条锈病"可能会被识别为"小麦 条锈病"
                    if ' ' in cleaned_pest_name:
                        space_removed_name = cleaned_pest_name.replace(' ', '')
                        space_matches = Pest.objects.filter(name__iexact=space_removed_name)
                        if space_matches.exists():
                            logger.info(f"空格移除后匹配成功: {cleaned_pest_name} -> {space_removed_name}")
                            # 在API响应中添加识别信息
                            api_response['extracted_info'] = {
                                'pest_name': pest_name,
                                'matched_name': space_removed_name,
                                'confidence': confidence,
                                'full_response': content,
                                'markdown_response': formatted_content,
                                'multiple_diseases': multiple_diseases if multiple_diseases else None
                            }
                            return space_matches.first(), confidence, api_response, model, response_time
                    
                    # 3. 特殊处理"锈病"类型的匹配问题
                    if '锈病' in pest_name:
                        # 提取宿主植物名称（如"小麦"）
                        host_match = re.match(r'(.+?)(?:条|杆|叶|茎|黄|褐)?锈病', pest_name)
                        if host_match:
                            host_name = host_match.group(1)
                            logger.info(f"检测到锈病，宿主植物: {host_name}")
                            
                            # 尝试匹配包含宿主名称和"锈病"的所有病虫害
                            from django.db.models import Q
                            rust_matches = Pest.objects.filter(
                                Q(name__icontains=host_name) & 
                                Q(name__icontains='锈病')
                            )
                            
                            if rust_matches.exists():
                                best_rust_match = rust_matches.first()
                                # 如果有多个匹配，查找最相似的
                                if rust_matches.count() > 1:
                                    best_similarity = 0
                                    for rm in rust_matches:
                                        sim = _calculate_name_similarity(pest_name, rm.name)
                                        if sim > best_similarity:
                                            best_similarity = sim
                                            best_rust_match = rm
                                
                                logger.info(f"锈病特殊匹配: {pest_name} -> {best_rust_match.name}")
                                # 在API响应中添加识别信息
                                api_response['extracted_info'] = {
                                    'pest_name': pest_name,
                                    'matched_name': best_rust_match.name,
                                    'confidence': confidence * 0.95,
                                    'full_response': content,
                                    'markdown_response': formatted_content,
                                    'multiple_diseases': multiple_diseases if multiple_diseases else None
                                }
                                return best_rust_match, confidence * 0.95, api_response, model, response_time
                    
                    # 4. 部分匹配（比如"小麦叶枯病"可以匹配"小麦赤霉叶枯病"）
                    # 查询本地数据库中匹配的病虫害
                    matching_pests = Pest.objects.filter(name__icontains=cleaned_pest_name)
                    if matching_pests.exists():
                        # 选择匹配度最高的结果
                        best_match = None
                        highest_similarity = 0
                        
                        for pest in matching_pests:
                            # 计算名称相似度
                            similarity = _calculate_name_similarity(pest_name, pest.name)
                            if similarity > highest_similarity:
                                highest_similarity = similarity
                                best_match = pest
                        
                        if best_match:
                            logger.info(f"名称相似度匹配: {pest_name} -> {best_match.name} (相似度: {highest_similarity:.2f})")
                            return best_match, confidence * highest_similarity, api_response, model, response_time
                    
                    # 5. 如果没有合适的匹配，尝试关键字匹配
                    name_parts = cleaned_pest_name.split()
                    for part in name_parts:
                        if len(part) >= 2:  # 跳过太短的词
                            keyword_matches = Pest.objects.filter(name__icontains=part)
                            if keyword_matches.exists():
                                logger.info(f"关键词匹配: {pest_name} -> {keyword_matches.first().name} (关键词: {part})")
                                return keyword_matches.first(), confidence * 0.85, api_response, model, response_time
                
                # 如果API没有返回有效结果或解析失败，但有内容
                if content:
                    api_response['extracted_info'] = {
                        'pest_name': pest_name,  # 可能为None
                        'confidence': confidence,
                        'full_response': content,
                        'markdown_response': formatted_content,
                        'multiple_diseases': multiple_diseases if multiple_diseases else None,
                        'has_recognition': pest_name is not None  # 指示是否有识别结果但未匹配到数据库
                    }
                
            except Exception as e:
                logger.exception(f"解析通义千问响应时出错: {str(e)}")
                
            return None, 0.0, api_response, model, response_time
            
        else:
            # API请求失败
            logger.error(f"API请求失败: {response.status_code} - {response.text}")
            return _mock_recognition(include_api_error=True, status_code=response.status_code)
            
    except Exception as e:
        # 捕获所有异常，确保不会因为API调用失败而影响用户体验
        logger.exception(f"识别过程异常: {str(e)}")
        return _mock_recognition(include_api_error=True, error_message=str(e))

def _calculate_context_score(text, pest_name):
    """评估病虫害名称在文本中的上下文相关性
    
    Args:
        text: 包含病虫害名称的文本段落
        pest_name: 病虫害名称
        
    Returns:
        float: 上下文相关性得分，范围0-1
    """
    base_score = 0.6  # 基础分
    
    # 关键词加分 - 在段落中发现的关键词增加相关性
    context_keywords = ['症状', '特征', '危害', '防治', '病毒', '病菌', '虫害', 
                        '叶片', '黄化', '发黄', '卷曲', '斑点', '枯萎', '干枯']
    keyword_score = 0
    for keyword in context_keywords:
        if keyword in text:
            keyword_score += 0.02  # 每个关键词加0.02分
    
    # 位置加分 - 名称出现在段落开头的加分更多
    position_score = 0
    name_position = text.find(pest_name)
    if name_position != -1:
        relative_position = name_position / len(text)
        if relative_position < 0.2:  # 靠近开头
            position_score = 0.1
        elif relative_position < 0.5:  # 在前半部分
            position_score = 0.05
    
    # 重复性加分 - 名称多次出现增加相关性
    occurrences = text.count(pest_name)
    repetition_score = min(0.05 * occurrences, 0.15)  # 最多加0.15分
    
    # 计算总分，最大为1.0
    total_score = min(base_score + keyword_score + position_score + repetition_score, 1.0)
    
    return total_score

def _calculate_name_similarity(name1, name2):
    """计算两个名称之间的相似度，返回0-1之间的相似度分数"""
    # 清理名称，移除空格和标点
    name1 = re.sub(r'[^\w]', '', name1.lower())
    name2 = re.sub(r'[^\w]', '', name2.lower())
    
    # 如果一个名称是另一个的子串，给予高相似度
    if name1 in name2:
        return 0.9 * (len(name1) / len(name2))
    if name2 in name1:
        return 0.9 * (len(name2) / len(name1))
    
    # 计算最长公共子序列 (LCS)
    def lcs_length(s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    # 计算Levenshtein距离（编辑距离）
    def levenshtein_distance(s1, s2):
        if not s1: return len(s2)
        if not s2: return len(s1)
        
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # 删除
                    dp[i][j-1] + 1,      # 插入
                    dp[i-1][j-1] + cost  # 替换
                )
        
        return dp[m][n]
    
    # 两种方法的结合评分
    lcs = lcs_length(name1, name2)
    max_len = max(len(name1), len(name2))
    lcs_similarity = lcs / max_len if max_len > 0 else 0
    
    distance = levenshtein_distance(name1, name2)
    levenshtein_similarity = 1 - (distance / max_len) if max_len > 0 else 0
    
    # 组合得分 (70% LCS + 30% Levenshtein)
    return lcs_similarity * 0.7 + levenshtein_similarity * 0.3

def _mock_recognition(include_api_error=False, status_code=None, error_message=None):
    """提供模拟的识别结果，用于API未配置或请求失败的情况"""
    all_pests = Pest.objects.all()
    model = API_CONFIG['model']
    response_time = random.uniform(0.5, 2.0)
    
    # 如果数据库中有病虫害记录
    if all_pests.exists():
        pest = random.choice(all_pests)
        confidence = random.uniform(0.65, 0.98)  # 随机生成0.65-0.98之间的置信度
        
        # 创建更复杂的模拟Markdown响应
        mock_markdown = f"""
# 病虫害识别结果

## 名称
{pest.name}

## 类型
{pest.get_type_display()}

## 症状
{pest.symptoms if hasattr(pest, 'symptoms') and pest.symptoms else '模拟症状数据：叶片出现黄斑、卷曲或枯萎等现象。'}

## 危害程度
{pest.get_severity_display() if hasattr(pest, 'severity') else '中等'}

## 防治建议
1. 加强农田管理，保持环境通风干燥
2. 合理施肥，增强植株抵抗力
3. 及时清除病残体和杂草
4. 使用专业农药进行防治

详细信息请参考病虫害详情页面。
"""
        
        # 创建模拟的API响应
        api_response = {
            'success': not include_api_error,
            'mock': True,
            'pest_name': pest.name,
            'confidence': confidence,
            'extracted_info': {
                'pest_name': pest.name,
                'confidence': confidence,
                'full_response': f"这是一个模拟识别结果，识别到的病虫害为：{pest.name}。\n\n病害特征：模拟数据\n\n防治方法：请参考详细页面。",
                'markdown_response': mock_markdown
            }
        }
        
        # 如果需要包含API错误信息
        if include_api_error:
            api_response.update({
                'error': True,
                'status_code': status_code,
                'message': error_message or '无法连接到识别API，使用本地模拟结果'
            })
            
        return pest, confidence, api_response, model, response_time
    
    # 如果数据库中没有病虫害记录
    api_response = {
        'success': False, 
        'mock': True, 
        'message': '数据库中没有病虫害记录',
        'extracted_info': {
            'full_response': "无法提供识别结果，因为数据库中没有病虫害记录可供匹配。"
        }
    }
    return None, 0.0, api_response, model, response_time

@require_http_methods(["GET", "POST"])
def recognition_view(request):
    """病虫害识别主页面"""
    if request.method == "POST":
        # 调试输出
        logger.info(f"接收到POST请求: {request.POST}")
        logger.info(f"文件: {request.FILES}")
        
        if 'image' in request.FILES:
            image = request.FILES['image']
            
            # 验证文件类型
            if not image.content_type.startswith('image/'):
                messages.error(request, "请上传有效的图片文件 (JPG, PNG等)")
                return redirect('pest_recognition:upload')
            
            # 验证文件大小（最大10MB）
            if image.size > 10 * 1024 * 1024:
                messages.error(request, "图片文件过大，请上传10MB以内的图片")
                return redirect('pest_recognition:upload')
            
            # 获取选择的模型
            selected_model = request.POST.get('model')
            logger.info(f"使用模型: {selected_model}")
            
            # 保存上传的图片 - 修复文件路径问题
            from datetime import datetime
            # 确保目录结构
            current_date = datetime.now()
            upload_dir = f'recognition_images/{current_date.year}/{str(current_date.month).zfill(2)}'
            upload_path = os.path.join('media', upload_dir)
            
            # 确保目录存在
            if not os.path.exists(upload_path):
                os.makedirs(upload_path, exist_ok=True)
            
            try:
                # 处理文件名，避免特殊字符
                import re
                safe_filename = re.sub(r'[^\w\.\-]', '_', image.name)
                image_name = f"{current_date.strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                image_path = default_storage.save(f'{upload_dir}/{image_name}', ContentFile(image.read()))
                saved_image = default_storage.open(image_path)
                
                # 识别图片
                logger.info(f"开始识别图片: {image_path}")
                try:
                    result_pest, confidence, api_response, model_used, response_time = recognize_image(saved_image, selected_model)
                    logger.info(f"识别完成，结果: {result_pest}, 置信度: {confidence}")
                    
                    # 获取AI识别的名称
                    ai_result_name = api_response.get('extracted_info', {}).get('pest_name')
                    has_db_match = result_pest is not None
                    
                    # 保存识别历史
                    history = RecognitionHistory(
                        user=request.user if request.user.is_authenticated else None,
                        image=image_path,
                        result_pest=result_pest,
                        confidence=confidence * 100,  # 将小数转为百分数
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        api_response=api_response,
                        model_used=model_used,
                        response_time=response_time,
                        ai_result_name=ai_result_name,
                        has_db_match=has_db_match
                    )
                    history.save()
                    
                    # 更新模型统计
                    history.update_model_stats()
                    
                    # 返回结果页面
                    return render(request, 'pest_recognition/result.html', {
                        'history': history,
                        'related_pests': Pest.objects.filter(type=result_pest.type)[:5] if result_pest else [],
                        'api_response': api_response
                    })
                    
                except Exception as e:
                    logger.exception(f"识别过程出错: {str(e)}")
                    messages.error(request, f"识别处理失败: {str(e)}")
                    return redirect('pest_recognition:upload')
                    
            except Exception as e:
                logger.exception(f"保存图片出错: {str(e)}")
                messages.error(request, f"无法处理上传的图片: {str(e)}")
                return redirect('pest_recognition:upload')
        else:
            messages.error(request, "请选择一张图片进行识别")
            return redirect('pest_recognition:upload')
    
    # GET请求显示上传页面
    recent_histories = []
    if request.user.is_authenticated:
        recent_histories = RecognitionHistory.objects.filter(
            user=request.user
        ).order_by('-create_time')[:4]  # 显示4个最近记录
    
    # 获取可用模型列表
    available_models = API_CONFIG.get('available_models', {})
    
    return render(request, 'pest_recognition/upload.html', {
        'recent_histories': recent_histories,
        'api_enabled': API_CONFIG.get('enabled', False),
        'available_models': available_models,
        'default_model': API_CONFIG.get('model'),
        'model_guide': MODEL_SELECTION_GUIDE,
    })

@method_decorator(login_required, name='dispatch')
class HistoryListView(ListView):
    """用户识别历史列表"""
    model = RecognitionHistory
    template_name = 'pest_recognition/history.html'
    context_object_name = 'histories'
    paginate_by = 12
    
    def get_queryset(self):
        return RecognitionHistory.objects.filter(user=self.request.user).order_by('-create_time')

@method_decorator(login_required, name='dispatch')
class HistoryDetailView(DetailView):
    """识别历史详情"""
    model = RecognitionHistory
    template_name = 'pest_recognition/result_detail.html'
    context_object_name = 'history'
    
    def get_queryset(self):
        """确保用户只能查看自己的识别历史"""
        return RecognitionHistory.objects.filter(user=self.request.user)

@require_http_methods(["POST"])
def api_recognize(request):
    """REST API接口，用于移动应用等"""
    if not request.FILES.get('image'):
        return JsonResponse({'error': '没有上传图片'}, status=400)
        
    image = request.FILES['image']
    
    # 保存上传的图片
    image_path = default_storage.save(f'temp_recognition/{image.name}', ContentFile(image.read()))
    saved_image = default_storage.open(image_path)
    
    try:
        # 识别图片
        results = recognize_image(saved_image)
        if len(results) == 5:  # 新版本返回5个参数
            result_pest, confidence, api_response, model_used, response_time = results
        else:  # 旧版本返回3个参数
            result_pest, confidence, api_response = results
            model_used = API_CONFIG['model']
            response_time = 0.0
        
        # 获取AI识别的名称
        ai_result_name = api_response.get('extracted_info', {}).get('pest_name')
        has_db_match = result_pest is not None
        
        # 保存识别历史
        history = RecognitionHistory(
            user=request.user if request.user.is_authenticated else None,
            image=image_path,
            result_pest=result_pest,
            confidence=confidence * 100,  # 将小数转为百分数
            ip_address=request.META.get('REMOTE_ADDR'),
            api_response=api_response,
            model_used=model_used,
            response_time=response_time,
            ai_result_name=ai_result_name,  # 保存AI识别的名称
            has_db_match=has_db_match      # 是否在数据库中匹配到
        )
        history.save()
        
        # 更新模型统计
        history.update_model_stats()
        
        # 返回JSON结果
        result = {
            'success': True,
            'history_id': history.id,
            'api_response': api_response
        }
        
        if result_pest:
            result.update({
                'pest_id': result_pest.id,
                'pest_name': result_pest.name,
                'pest_type': result_pest.get_type_display(),
                'confidence': confidence*100,  # 确保这里的置信度也乘以100
                'detail_url': f'/orange/pest/{result_pest.id}/'
            })
        else:
            # 增强无法识别时返回的信息
            result.update({
                'pest_id': None,
                'message': '无法识别病虫害，请尝试使用更清晰的图片',
                'raw_content': api_response.get('choices', [{}])[0].get('message', {}).get('content', '') if 'choices' in api_response else '无内容',
                'ai_recognized_name': api_response.get('extracted_info', {}).get('pest_name'),  # 添加AI识别的名称
                'has_recognition': api_response.get('extracted_info', {}).get('has_recognition', False),  # 是否有AI识别结果
                'diagnosis': {
                    'reason': '无法从API响应中提取有效的病虫害信息或数据库中没有匹配项',
                    'suggestions': [
                        '请确保图片中病害症状清晰可见',
                        '尝试从不同角度拍摄病害部位',
                        '在光线充足的环境下拍摄',
                        '选择更高级的识别模型'
                    ]
                }
            })
            
        return JsonResponse(result)
        
    except Exception as e:
        logger.exception(f"API识别请求处理异常: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
