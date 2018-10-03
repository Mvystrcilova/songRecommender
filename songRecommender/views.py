from django.shortcuts import render
from django.views import generic
from songRecommender.models import Song, List, Song_in_List, Played_Song, Distance_to_User, Distance_to_List, Distance

# Create your views here.

# def index(request):
#    songs = Song.objects.all().count()

#    context = {
#       'songs': songs
#    }

#    return render(request, 'songRecommender/index.html', context=context)

class HomePageView(generic.ListView):
    context_object_name = 'home_list'
    queryset = Song.objects.all()[:10]
    template_name = 'songRecommender/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.all()[:10]
        return context

class AddSongView(generic.ListView):
    model = Song
    template_name = 'songRecommender/addSong.html'