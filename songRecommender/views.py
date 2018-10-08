from django.shortcuts import render
from django.views import generic
from songRecommender.models import Song, List, Song_in_List, Played_Song, Distance_to_User, Distance_to_List, Distance
from django.contrib.auth.mixins import LoginRequiredMixin
from itertools import chain


# Create your views here.

class HomePageView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'home_list'
    queryset = Song.objects.all()
    template_name = 'songRecommender/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)
        return context


class AddSongView(generic.ListView):
    model = Song
    template_name = 'songRecommender/addSong.html'


class SongDetailView(generic.DetailView):
    model = Song
    template_name = 'songRecommender/song_detail.html'


class ListDetailView(LoginRequiredMixin, generic.DetailView):
    model = List
    template_name = 'songRecommender/list_detail.html'
    paginate_by = 10

    def get_queryset(self):
        return List.objects.filter(user_id=self.request.user)


class MyListsView(LoginRequiredMixin, generic.ListView):
    model = List
    template_name = 'songRecommender/my_lists.html'
    context_object_name = 'moje_listy'
    paginate_by = 10

    def get_queryset(self):
        return List.objects.filter(user_id=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MyListsView, self).get_context_data(**kwargs)
        context['played_songs'] = Played_Song.objects.filter(user_id=self.request.user)

        return context

class RecommendedSongsView(generic.ListView):
    model = Song
    template_name = 'songRecommender/recommended_songs.html'
