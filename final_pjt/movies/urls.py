from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_pk>/', views.detail, name='detail'),
    path('<int:movie_pk>/rank_save/', views.rank_save, name='rank_save'),
    path('<int:movie_pk>/rank_delete/', views.rank_delete, name='rank_delete'),
    path('<int:movie_pk>/create/', views.create, name='create'),
    path('<int:movie_pk>/<int:review_pk>/update/', views.update, name='update'),
    path('<int:movie_pk>/<int:review_pk>/delete/', views.delete, name='delete'),
    path('<int:movie_pk>/<int:review_pk>/like/', views.like, name='like'),
    path('<int:movie_pk>/<int:review_pk>/hate/', views.hate, name='hate'),
    path('<int:movie_pk>/<int:review_pk>', views.review_detail, name='review_detail'),
    path('<int:movie_pk>/<int:review_pk>/create/', views.comment_create, name='comment_create'),
    path('<int:movie_pk>/<int:review_pk>/<int:comment_pk>/update/', views.comment_update, name='comment_update'),
    path('<int:movie_pk>/<int:review_pk>/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
]