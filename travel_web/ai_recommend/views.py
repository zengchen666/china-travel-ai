from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from attractions.models import City, Attraction
from users.models import TravelHistory
from ai_recommend.rag import retrieve as rag_retrieve
import json
import requests
import re


def recommend_page(request):
    cities = City.objects.all().order_by('name')
    # 获取用户的历史记录
    history = []
    if request.user.is_authenticated:
        history = TravelHistory.objects.filter(user=request.user)[:5]
    return render(request, 'ai_recommend/recommend.html', {'cities': cities, 'history': history})


from django.contrib.auth.decorators import login_required

@login_required
def history_page(request):
    history = TravelHistory.objects.filter(user=request.user)
    return render(request, 'ai_recommend/history.html', {'history': history})


@csrf_exempt
@require_POST
def get_recommendation(request):
    try:
        data = json.loads(request.body)
        city = data.get('city', '').strip()
        preferences = data.get('preferences', '').strip()
        season = data.get('season', '春季')
        days = data.get('days', 3)
        budget = data.get('budget', 3000)

        if not city and not preferences:
            return JsonResponse({'success': False, 'error': '请选择目标城市或填写旅行偏好'})

        # RAG 检索：按用户偏好从全库召回最相关的景点（城市可选过滤）
        query_parts = []
        if preferences:
            query_parts.append(preferences)
        if city:
            query_parts.append(f'{city}旅游')
        query_parts.append(f'{season}出游')
        query_text = '，'.join(query_parts)

        attractions = rag_retrieve(query_text, city=city or None, top_k=15)
        if not attractions:
            # 检索失败兜底：按评分取该城市/全库 TOP15
            qs = Attraction.objects.all()
            if city:
                qs = qs.filter(city__name=city)
            attractions = list(qs.order_by('-score', '-comment_count')[:15])

        if not attractions:
            return JsonResponse({'success': False, 'error': '景点库为空，请先导入数据'})

        attractions_info = "\n".join([
            f"- {a.name}（{a.city.name if a.city else '未知城市'}，评分:{a.score}, "
            f"票价:{a.price or '免费'}, 评论数:{a.comment_count}）"
            for a in attractions
        ])
        preference_line = f"用户偏好：{preferences}\n" if preferences else ""
        city_line = city if city else "不限（请根据用户偏好与下列候选景点选择最合适的城市）"

        # 构建提示词
        prompt = f"""你是一个专业的旅游规划师。请根据以下信息为用户规划一个详细的旅游路线：

目标城市：{city_line}
{preference_line}旅游季节：{season}
行程天数：{days}天
预算：{budget}元

根据用户需求从景点库中检索到的候选景点（已按相关度排序）：
{attractions_info}

请提供：
1. 每天的详细行程安排（包含具体景点、游玩时间、交通方式）
2. 餐饮推荐（当地特色美食）
3. 住宿建议
4. 预算分配建议
5. 注意事项和小贴士

请用中文回答，格式清晰，使用emoji让内容更生动。

最后，请从上述景点中选择你推荐的3-5个核心景点，用以下JSON格式输出（放在回答最后）：
[ATTRACTIONS_JSON]
["景点名1", "景点名2", "景点名3"]
[/ATTRACTIONS_JSON]
"""
        
        # 调用 DeepSeek API
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key or api_key == 'your_deepseek_api_key':
            return JsonResponse({'success': False, 'error': 'DeepSeek API Key 未配置'})
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    'https://api.deepseek.com/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'deepseek-chat',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.7,
                        'max_tokens': 2000
                    },
                    timeout=90
                )
                
                if response.status_code == 200:
                    break
                elif attempt < max_retries - 1:
                    import time
                    time.sleep(2)
                    continue
                else:
                    return JsonResponse({'success': False, 'error': f'API请求失败，请稍后重试'})
            except requests.Timeout:
                if attempt < max_retries - 1:
                    continue
                return JsonResponse({'success': False, 'error': 'AI响应超时，请重试'})
        
        if response.status_code != 200:
            return JsonResponse({'success': False, 'error': f'API请求失败: {response.status_code}'})
        
        result = response.json()
        recommendation = result['choices'][0]['message']['content']
        
        # 提取推荐的景点名称
        map_points = []
        json_match = re.search(r'\[ATTRACTIONS_JSON\](.*?)\[/ATTRACTIONS_JSON\]', recommendation, re.DOTALL)
        if json_match:
            try:
                recommended_names = json.loads(json_match.group(1).strip())
                # 清理输出中的JSON标记
                recommendation = re.sub(r'\[ATTRACTIONS_JSON\].*?\[/ATTRACTIONS_JSON\]', '', recommendation, flags=re.DOTALL).strip()
                
                # 获取景点的经纬度（城市不限时按名称全库匹配）
                for name in recommended_names:
                    qs = Attraction.objects.filter(name__icontains=name)
                    if city:
                        qs = qs.filter(city__name=city)
                    attr = qs.first()
                    if attr and attr.longitude and attr.latitude:
                        map_points.append({
                            'name': attr.name,
                            'lng': float(attr.longitude),
                            'lat': float(attr.latitude),
                            'score': float(attr.score) if attr.score else 0
                        })
            except:
                pass
        
        # 保存推荐历史（如果用户已登录）
        if request.user.is_authenticated:
            TravelHistory.objects.create(
                user=request.user,
                city=city or '智能匹配',
                season=season,
                days=days,
                budget=budget,
                recommendation=recommendation
            )
        
        return JsonResponse({
            'success': True,
            'recommendation': recommendation,
            'map_points': map_points,
            'city': city
        })
        
    except requests.Timeout:
        return JsonResponse({'success': False, 'error': 'AI响应超时，请重试'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
