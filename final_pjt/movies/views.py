from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Movie, Genre, Review, Comment, Rank
from .forms import ReviewForm, CommentForm

import random
# Create your views here.
def index(request):
    movies = Movie.objects.all()
    #Random
    moviesRandom = random.sample(list(movies),18)
    movies_1=moviesRandom[:6]
    movies_2=moviesRandom[6:12]
    movies_3=moviesRandom[12:]
    context ={
        'movies_1':movies_1,
        'movies_2': movies_2,
        'movies_3': movies_3,
    # 1. 사용자가 7점이상 평점을 준 영화 중 가장 많은 장르의 영화를 추천
    # 사용자가 로그인하고 평점을 준 영화가 있을 경우 (이미 평점을 준 영화 제외)
    # 목록이 12개가 안되면 모든 장르 영화 중 인기도순으로 채워넣는다.
    highrank_genre = []
    if request.user.is_authenticated and Rank.objects.all().filter(user=request.user, num__gte=7).exists():
        ranks = Rank.objects.all().filter(user=request.user, num__gte=7)
        genres_dic = {}
        for rank in ranks:
            movie = rank.movie
            for genre in movie.genres.all():
                if genre.name in genres_dic:
                    genres_dic[genre.id] += 1
                else:
                    genres_dic[genre.id] = 1
        genres_sort = sorted(genres_dic.items(), key=lambda x:x[1], reverse=True)
        most_liked_genre = genres_sort[0][0]
        # 그 장르 중 인지도가 높은 순으로
        for movie in Movie.objects.order_by('-popularity'):
            if not Rank.objects.all().filter(user=request.user, movie=movie).exists():
                for genre in movie.genres.all():
                    if most_liked_genre == genre.id:
                        highrank_genre.append(movie)
                        if len(highrank_genre)==12:
                            break
                if len(highrank_genre)==12:
                    break
    if len(highrank_genre)<12:
        for movie in Movie.objects.order_by('-popularity'):
            if not Rank.objects.all().filter(user=request.user, movie=movie).exists():
                highrank_genre.append(movie)
                if len(highrank_genre)==12:
                    break

    highrank_genre_front = highrank_genre[:6]
    highrank_genre_end = highrank_genre[6:12]

    # 2. 최근 사용자가 평점을 준 영화들
    # 최근 평점을 준 순서대로 추출
    # index.html에 '사용자가 로그인을 했으면'이라는 조건 필요
    recent_movies = []
    if Rank.objects.all().filter(user=request.user).exists():
        ranks = Rank.objects.all().filter(user=request.user).order_by('-pk')
        for rank in ranks:
            movie = rank.movie
            recent_movies.append(movie)
            if len(recent_movies)==12:
                break
    if recent_movies:
        recent_movies_front = recent_movies[:6]
        if len(recent_movies)>6:
            recent_movies_end = recent_movies[6:]
        else:
            recent_movies_end = []
    else:
        recent_movies_front = []
        recent_movies_end = []

    # 3. 높은 평점을 가진 영화 순서대로(기존 json 파일에 있는 평균평점이용)
    # 기존 Movie 모델에 있는 속성으로만 바꿔주면 그에 맞는 알고리즘이 된다.
    highvote_movies = Movie.objects.order_by('-vote_average')[:12]
    highvote_movies_front = highvote_movies[:6]
    highvote_movies_end = highvote_movies[6:]

    context = {
        'highrank_genre_front' : highrank_genre_front,
        'highrank_genre_end' : highrank_genre_end,
        'recent_movies_front' : recent_movies_front,
        'recent_movies_end' : recent_movies_end,
        'highvote_movies_front' : highvote_movies_front,
        'highvote_movies_end' : highvote_movies_end,
    }
    return render(request, 'movies/index.html', context)

def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk = movie_pk)
    rank_num = 0
    if request.user.is_authenticated:
        if Rank.objects.all().filter(movie=movie, user=request.user).exists():
            rank = get_object_or_404(Rank, movie=movie, user=request.user)
            rank_num = rank.num
    ranks = Rank.objects.all().filter(movie=movie)
    sum_ranks = 0
    cnt_ranks = 0
    for rank in ranks:
        sum_ranks += rank.num
        cnt_ranks += 1
    if cnt_ranks:
        avg_rank = round(sum_ranks/cnt_ranks, 1)
    else:
        avg_rank = 0
    reviews = movie.review_set.all().order_by('-pk')
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'avg_rank' : avg_rank,
        'movie' : movie,
        'page_obj' : page_obj,
        'rank_num' : [1]*rank_num+[0]*(10-rank_num)
    }
    return render(request, 'movies/detail.html', context)

@login_required
def create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            return redirect('movies:review_detail', movie.pk, review.pk)
    else:
        form = ReviewForm()
    context = {
        'form' : form,
        'movie' : movie,
    }
    return render(request, 'movies/form.html', context)

@login_required
@require_POST
def rank_save(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if Rank.objects.all().filter(movie=movie, user=user).exists():
        rank = get_object_or_404(Rank, movie=movie, user=user)
    else:
        rank = Rank(movie=movie, user=user)
    num = request.POST.get('num', None)
    rank.num = num
    rank.save()
    return JsonResponse({})

@login_required
@require_POST
def rank_delete(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if Rank.objects.all().filter(movie=movie, user=user).exists():
        rank = get_object_or_404(Rank, movie=movie, user=user)
        rank.delete()
    return JsonResponse({})

@login_required
def update(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user==review.user:
        if request.method=='POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()
                return redirect('movies:review_detail', movie.pk, review.pk)
        else:
            form = ReviewForm(instance=review)
        context = {
            'review' : review,
            'movie' : movie,
            'form' : form
        }
        return render(request, 'movies/form.html', context)
    else:
        return redirect('movies:review_detail', movie.pk, review.pk)

@login_required
def delete(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user==review.user:
        review.delete()
    else:
        return redirect('movies:review_detail', movie.pk, review.pk)
    return redirect('movies:detail', movie.pk)

@login_required
def like(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    movie = get_object_or_404(Movie, pk=movie_pk)
    if review.like_users.filter(id=request.user.pk).exists():
        review.like_users.remove(request.user)
        liked = False
        hated = False
    elif review.hate_users.filter(id=request.user.pk).exists():
        review.hate_users.remove(request.user)
        review.like_users.add(request.user)
        liked = True
        hated = True
    else:
        review.like_users.add(request.user)
        liked = True
        hated = False
    return JsonResponse({
        'liked' : liked,
        'hated' : hated,
        'like_count' : review.like_users.count(),
        'hate_count' : review.hate_users.count(),
    })

@login_required
def hate(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    movie = get_object_or_404(Movie, pk=movie_pk)
    if review.hate_users.filter(id=request.user.pk).exists():
        review.hate_users.remove(request.user)
        liked = False
        hated = False
    elif review.like_users.filter(id=request.user.pk).exists():
        review.like_users.remove(request.user)
        review.hate_users.add(request.user)
        liked = True
        hated = True
    else:
        review.hate_users.add(request.user)
        liked = False
        hated = True
    return JsonResponse({
        'liked' : liked,
        'hated' : hated,
        'like_count' : review.like_users.count(),
        'hate_count' : review.hate_users.count(),
    })

def review_detail(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    form = CommentForm()
    context = {
        'movie' : movie,
        'review' : review,
        'form' : form,
    }
    return render(request, 'movies/review_detail.html', context)

@login_required
@require_POST
def comment_create(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.review = review
        comment.save()
    return redirect('movies:review_detail', movie.pk, review.pk)

@login_required
def comment_update(request, movie_pk, review_pk, comment_pk):
    review = get_object_or_404(Review, pk=review_pk)
    movie = get_object_or_404(Movie, pk=movie_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.method=='POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.review = review
            comment.save()
            return redirect('movies:review_detail', movie.pk, review.pk)
    else:
        form = CommentForm(instance=comment)
    context = {
        'review' : review,
        'movie' : movie,
        'form' : form
    }
    return render(request, 'movies/form.html', context)

@login_required
def comment_delete(request, movie_pk, review_pk, comment_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user==comment.user:
        comment.delete()
    return redirect('movies:review_detail', movie.pk, review_pk)