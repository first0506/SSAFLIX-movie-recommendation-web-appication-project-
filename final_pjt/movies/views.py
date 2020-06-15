from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Movie, Genre, Review, Comment, Rank
from .forms import ReviewForm, CommentForm

# Create your views here.
def index(request):
    return render(request, 'movies/index.html')

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