from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from attractions.models import Attraction, Province, City


def dashboard(request):
    return render(request, 'visualization/dashboard.html')


def score_distribution(request):
    """景点评分分布"""
    data = []
    ranges = [('5分', 4.5, 5.1), ('4-4.5分', 4, 4.5), ('3.5-4分', 3.5, 4), ('3-3.5分', 3, 3.5), ('3分以下', 0, 3)]
    for label, min_s, max_s in ranges:
        count = Attraction.objects.filter(score__gte=min_s, score__lt=max_s).count()
        if count > 0:
            data.append({'name': label, 'value': count})
    return JsonResponse({'data': data})


def province_avg_score(request):
    """各省份平均评分"""
    data = Province.objects.annotate(
        avg_score=Avg('city__attraction__score')
    ).filter(avg_score__isnull=False).values('name', 'avg_score').order_by('-avg_score')
    return JsonResponse({
        'provinces': [d['name'] for d in data],
        'scores': [round(d['avg_score'], 2) for d in data]
    })


def top_comments(request):
    """评论数排行TOP10"""
    data = Attraction.objects.order_by('-comment_count')[:10].values('name', 'comment_count')
    return JsonResponse({
        'names': [d['name'] for d in data],
        'counts': [d['comment_count'] for d in data]
    })


def city_hot_attractions(request):
    """城市热门景点"""
    city_name = request.GET.get('city', '')
    if city_name:
        attractions = Attraction.objects.filter(city__name__icontains=city_name)
    else:
        attractions = Attraction.objects.all()
    attractions = attractions.order_by('-comment_count')[:10]
    data = [{'name': a.name, 'score': float(a.score) if a.score else 0,
             'comments': a.comment_count, 'lng': float(a.longitude) if a.longitude else 0,
             'lat': float(a.latitude) if a.latitude else 0} for a in attractions]
    return JsonResponse({'data': data})


def province_count(request):
    """各省份景点数量"""
    data = Province.objects.annotate(count=Count('city__attraction')).values('name', 'count').order_by('-count')
    return JsonResponse({
        'provinces': [d['name'] for d in data],
        'counts': [d['count'] for d in data]
    })


def price_distribution(request):
    """票价分布"""
    data = [
        {'name': '免费', 'value': Attraction.objects.filter(Q(price__isnull=True) | Q(price=0)).count()},
        {'name': '1-50元', 'value': Attraction.objects.filter(price__gt=0, price__lte=50).count()},
        {'name': '51-100元', 'value': Attraction.objects.filter(price__gt=50, price__lte=100).count()},
        {'name': '101-200元', 'value': Attraction.objects.filter(price__gt=100, price__lte=200).count()},
        {'name': '200元以上', 'value': Attraction.objects.filter(price__gt=200).count()},
    ]
    return JsonResponse({'data': [d for d in data if d['value'] > 0]})


def level_distribution(request):
    """景区等级分布"""
    levels = Attraction.objects.exclude(level='').values('level').annotate(count=Count('id')).order_by('-count')
    no_level = Attraction.objects.filter(level='').count()
    data = [{'name': d['level'], 'value': d['count']} for d in levels]
    if no_level > 0:
        data.append({'name': '未评级', 'value': no_level})
    return JsonResponse({'data': data})


def map_data(request):
    """地图标注数据"""
    attractions = Attraction.objects.exclude(longitude__isnull=True).exclude(latitude__isnull=True)
    data = [{'name': a.name, 'value': [float(a.longitude), float(a.latitude), a.comment_count],
             'city': a.city.name, 'score': float(a.score) if a.score else 0} for a in attractions]
    return JsonResponse({'data': data})


def stats_data(request):
    """统计数据"""
    from django.db.models import Sum
    total_attractions = Attraction.objects.count()
    total_cities = City.objects.count()
    total_provinces = Province.objects.count()
    avg_score = Attraction.objects.filter(score__isnull=False, score__gt=0).aggregate(avg=Avg('score'))['avg']
    return JsonResponse({
        'attractions': total_attractions,
        'cities': total_cities,
        'provinces': total_provinces,
        'avg_score': round(avg_score, 1) if avg_score else 4.5
    })
