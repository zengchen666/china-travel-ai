from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Attraction, City, Province


def index(request):
    hot_attractions = Attraction.objects.select_related('city', 'city__province').order_by('-comment_count')[:8]
    total_attractions = Attraction.objects.count()
    total_cities = City.objects.count()
    total_provinces = Province.objects.count()
    total_comments = Attraction.objects.aggregate(total=Sum('comment_count'))['total'] or 0
    return render(request, 'attractions/index.html', {
        'hot_attractions': hot_attractions,
        'total_attractions': total_attractions,
        'total_cities': total_cities,
        'total_provinces': total_provinces,
        'total_comments': total_comments / 10000,
    })


def attraction_list(request):
    attractions = Attraction.objects.select_related('city', 'city__province').all()
    province_id = request.GET.get('province')
    city_id = request.GET.get('city')
    sort = request.GET.get('sort', 'comments')
    if province_id:
        attractions = attractions.filter(city__province_id=province_id)
    if city_id:
        attractions = attractions.filter(city_id=city_id)
    if sort == 'score':
        attractions = attractions.order_by('-score')
    elif sort == 'price_low':
        attractions = attractions.order_by('price')
    elif sort == 'price_high':
        attractions = attractions.order_by('-price')
    else:
        attractions = attractions.order_by('-comment_count')
    paginator = Paginator(attractions, 12)
    attractions = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'attractions/list.html', {
        'attractions': attractions,
        'provinces': Province.objects.all(),
        'cities': City.objects.all(),
        'current_province': province_id,
        'current_city': city_id,
        'current_sort': sort,
    })


def attraction_detail(request, pk):
    attraction = get_object_or_404(Attraction.objects.select_related('city', 'city__province'), pk=pk)
    related = Attraction.objects.filter(city=attraction.city).exclude(pk=pk)[:4]
    is_favorited = False
    if request.user.is_authenticated:
        from users.models import Favorite
        is_favorited = Favorite.objects.filter(user=request.user, attraction=attraction).exists()
    return render(request, 'attractions/detail.html', {'attraction': attraction, 'related_attractions': related, 'is_favorited': is_favorited})


def search(request):
    keyword = request.GET.get('q', '').strip()
    if keyword:
        attractions = Attraction.objects.filter(Q(name__icontains=keyword) | Q(city__name__icontains=keyword) | Q(address__icontains=keyword))
    else:
        attractions = Attraction.objects.none()
    paginator = Paginator(attractions, 12)
    attractions = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'attractions/search.html', {'attractions': attractions, 'keyword': keyword})
