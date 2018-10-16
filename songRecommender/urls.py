from django.urls import path
from songRecommender import views


urlpatterns = [
    path('index/', views.HomePageView.as_view(), name='index'),
    path('addSong/', views.addSong, name='addSong'),
    path('song/<int:pk>', views.SongDetailView.as_view(), name='song_detail'),
    path('list/<int:pk>', views.ListDetailView.as_view(), name='list_detail'),
    path('mylists/', views.MyListsView.as_view(), name='my_lists'),
    path('recommended_songs/', views.RecommendedSongsView.as_view(), name='recommended_songs')
]

