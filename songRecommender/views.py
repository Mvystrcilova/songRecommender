from django.shortcuts import render
from django.views import generic
from songRecommender.models import Song, List, Song_in_List, Played_Song, Distance_to_User, Distance_to_List, Distance

# Create your views here.

class HomePageView(generic.ListView):
    context_object_name = 'home_list'
    queryset = Song.objects.all()
    template_name = 'songRecommender/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.all()
        return context

class AddSongView(generic.ListView):
    model = Song
    template_name = 'songRecommender/addSong.html'


class SongDetailView(generic.DetailView):
    model = Song
    template_name = 'songRecommender/song_detail.html'

class ListDetailView(generic.DetailView):
    model = List
    template_name = 'songRecommender/list_detail.html'

class MyListsView(generic.ListView):
    model = List
    template_name = 'songRecommender/my_lists.html'

class RecommendedSongsView(generic.ListView):
    model = Song
    template_name = 'songRecommender/recommended_songs.html'