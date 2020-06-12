from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Movie, Genre, Review, Comment

# Create your views here.
def index(request):
    return render(request, 'movies/index.html')

def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk = movie_pk)
    movies = Movie.objects.all()
    reviews = movie.review_set.all()
    paginator = Paginator(movies, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'movie' : movie,
        'page_obj' : page_obj,
    }
    return render(request, 'movies/detail.html', context)

def create(reqeust, movie_pk):
    pass

def update(request, movie_pk, review_pk):
    pass

def delete(request, movie_pk, review_pk):
    pass

def like(request, movie_pk, review_pk):
    pass

def hate(request, movie_pk, review_pk):
    pass

def review_detail(request, movie_pk, review_pk):
    pass

def comment_create(request, movie_pk, review_pk):
    pass

def comment_update(request, movie_pk, review_pk, comment_pk):
    pass

def comment_delete(request, movie_pk, review_pk, comment_pk):
    pass