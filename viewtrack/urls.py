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
]