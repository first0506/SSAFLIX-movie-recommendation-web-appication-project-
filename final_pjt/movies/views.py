from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Movie, Genre, Review, Comment
from .forms import ReviewForm, CommentForm

# Create your views here.
def index(request):
    pass

def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk = movie_pk)
    movies = Movie.objects.all()
    reviews = movie.review_set.all()
    paginator = Paginator(movies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'movie' : movie,
        'page_obj' : page_obj,
    }
    return render(request, 'movies/detail.html', context)

def create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = None
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