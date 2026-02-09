from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('progress/', views.ListViewTrackView.as_view(), name='progress-viewtrack'),
    path('progress/category/<str:category>/', views.ListViewTrackView.as_view(), name='category-viewtrack'),
    path('progress/<int:pk>/detail/', views.DetailViewTrackView.as_view(), name='detail-viewtrack'),
    path('progress/create/', views.CreateViewTrackView.as_view(), name='create-viewtrack'),
    path('progress/<int:pk>/delete/', views.DeleteViewTrackView.as_view(), name='delete-viewtrack'),
    path('progress/<int:pk>/update/', views.UpdateViewTrackView.as_view(), name='update-viewtrack'),
    path("episode/<int:pk>/update/", views.UpdateEpisodeProgressView.as_view(), name="episode-update"),
    path("episode/<int:pk>/delete/", views.DeleteEpisodeProgressView.as_view(), name="episode-delete"),
    path("episode/<int:episode_pk>/favorite/add/", views.CreateFavoriteView.as_view(), name="favorite-add"),
    path("favorite/<int:pk>/update/", views.UpdateFavoriteView.as_view(), name="favorite-update"),
    path("favorite/<int:pk>/delete/",views.DeleteFavoriteView.as_view(), name="favorite-delete"),
]