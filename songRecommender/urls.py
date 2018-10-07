from django.urls import path
from songRecommender import views


urlpatterns = [
    path('index/', views.HomePageView.as_view(), name='index'),
    path('addSong/', views.AddSongView.as_view(), name='addSong'),
    path('song/<int:pk>', views.SongDetailView.as_view(), name='song_detail'),
    path('list/<int:pk>', views.ListDetailView.as_view(), name='list_detail'),
    path('mylists/', views.MyListsView.as_view(), name='my_lists'),
]