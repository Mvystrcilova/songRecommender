from django.urls import path
from songRecommender import views
from django.conf.urls import url


urlpatterns = [
    path('index/', views.HomePageView.as_view(), name='index'),
    path('addSong/', views.addSong, name='addSong'),
    path('likeSong/<int:pk>', views.likeSong, name='likesong'),
    path('dislikeSong/<int:pk>', views.dislikeSong, name='dislikesong'),
    path('add_song_to_list/<int:pk>', views.add_song_to_list, name='add_song_to_list'),
    path('song/<int:pk>', views.SongDetailView.as_view(), name='song_detail'),
    path('list/<int:pk>', views.ListDetailView.as_view(), name='list_detail'),
    path('mylists/', views.MyListsView.as_view(), name='my_lists'),
    path('recommended_songs/', views.RecommendedSongsView.as_view(), name='recommended_songs')
]

urlpatterns += [
    path('list/create/', views.ListCreate.as_view(), name='list_create'),
    path('list/<int:pk>/update/', views.ListUpdate.as_view(), name='list_update'),
    path('list/<int:pk>/delete/', views.ListDelete.as_view(), name='list_delete'),
]

urlpatterns += [
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]