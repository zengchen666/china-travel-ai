from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, TravelHistory, Favorite
from attractions.models import Attraction


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('attractions:index')
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    return redirect('attractions:index')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email', '')
        if password != password2:
            messages.error(request, '两次密码不一致')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            login(request, user)
            messages.success(request, '注册成功')
            return redirect('attractions:index')
    return render(request, 'users/register.html')


@login_required
def profile(request):
    history = TravelHistory.objects.filter(user=request.user)[:10]
    favorites = Favorite.objects.filter(user=request.user).select_related('attraction', 'attraction__city')[:6]
    return render(request, 'users/profile.html', {'history': history, 'favorites': favorites})


@login_required
def add_favorite(request, attraction_id):
    attraction = get_object_or_404(Attraction, pk=attraction_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, attraction=attraction)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'created': created})
    messages.success(request, '收藏成功' if created else '已在收藏中')
    return redirect('attractions:detail', pk=attraction_id)


@login_required
def remove_favorite(request, attraction_id):
    Favorite.objects.filter(user=request.user, attraction_id=attraction_id).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, '已取消收藏')
    next_url = request.GET.get('next', 'users:favorites')
    return redirect(next_url)


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('attraction', 'attraction__city', 'attraction__city__province')
    return render(request, 'users/favorites.html', {'favorites': favorites})
