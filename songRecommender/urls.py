from django.urls import path
from songRecommender import views
from django.conf.urls import url, include

"""this module contains all urls that the app contains"""

urlpatterns = [
    path('index/', views.HomePageView.as_view(), name='index'),
    path('addSong/', views.addSong, name='addSong'),
    path('likeSong/<int:pk>', views.likeSong, name='likesong'),
    path('dislikeSong/<int:pk>', views.dislikeSong, name='dislikesong'),
    path('add_song_to_list/<int:pk>/<int:pk2>', views.add_song_to_list, name='add_song_to_list'),
    path('all_songs', views.AllSongsView.as_view(), name='all_songs'),
    path('song/<int:pk>', views.SongDetailView.as_view(), name='song_detail'),
    path('list/<int:pk>', views.ListDetailView.as_view(), name='list_detail'),
    path('mylists/', views.MyListsView.as_view(), name='my_lists'),
    path('recommended_songs/', views.RecommendedSongsView.as_view(), name='recommended_songs'),
    path('delete_account/', views.delete_account, name='delete_account')


]

urlpatterns += [
    path('list/create/', views.ListCreate.as_view(), name='list_create'),
    path('list/<int:pk>/update/', views.ListUpdate.as_view(), name='list_update'),
    path('list/<int:pk>/delete/', views.ListDelete.as_view(), name='list_delete'),
    path('add_to_list_failed/<int:pk>/<int:pk2>', views.add_to_list_failed, name='add_to_list_failed'),
    path('add_song_failed/<int:pk>', views.add_song_failed, name='add_song_failed'),
    path('about/', views.get_about, name='get_about')

]

urlpatterns += [
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^search_results/?$', views.search, name='search_results'),
    url(r'^change_distance/*', views.change_distance, name='change_distance'),
]