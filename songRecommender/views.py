from django.views import generic
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from songRecommender.Logic.Text_Shaper import get_TFidf_distance, save_distances
#from songRecommender.Logic.Text_Shaper import get_W2V_distance
from songRecommender.Logic.model_distances_calculator import save_list_distances, save_user_distances
from songRecommender.Logic.Recommender import check_if_in_played, change_youtube_url, recalculate_distances
from songRecommender.forms import SongModelForm, ListModelForm
from songRecommender.models import Song, List, Song_in_List, Played_Song, Distance_to_User, Distance_to_List, Distance, Profile

from .forms import SignUpForm
from .tokens import account_activation_token

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode



class HomePageView(LoginRequiredMixin, generic.ListView):
    """class showing the home page
    shows his lists and recommended songs to the user"""

    model = Distance_to_User
    context_object_name = 'home_list'
    template_name = 'songRecommender/index.html'

    def get_queryset(self):
        """:returns """
        played_songs = Played_Song.objects.all().filter(user_id=self.request.user.profile.pk).exclude(opinion=-1)[:10]
        return Distance_to_User.objects.filter(user_id=self.request.user.pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True))

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)
        return context


class SongDetailView(LoginRequiredMixin, generic.DetailView):
    """class creating a detail view for each song
    """
    model = Song
    template_name = 'songRecommender/song_detail.html'
    paginate_by = 10


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SongDetailView, self).get_context_data(**kwargs)
        check_if_in_played(context['object'].pk, self.request.user, is_being_played=True)
        context['played_song'] = Played_Song.objects.filter(
            song_id1=context['object'], user_id=self.request.user.profile)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)

        return context


class ListDetailView(LoginRequiredMixin, generic.DetailView):
    model = List
    template_name = 'songRecommender/list_detail.html'
    paginate_by = 10

    def get_queryset(self):
        return List.objects.filter(user_id=self.request.user)


class ListCreate(LoginRequiredMixin, CreateView):
    model = List
    fields = ['name']

    def post(self, request, *args, **kwargs):
        form = ListModelForm(data=request.POST)
        if form.is_valid():
            list = form.save(commit=False)
            list.user_id = request.user
            list.save()
        return HttpResponseRedirect(reverse('index'))


class ListUpdate(LoginRequiredMixin, UpdateView):
    model = List
    # fields = ['name']


class ListDelete(LoginRequiredMixin, DeleteView):
    model = List
    success_url = reverse_lazy('my_lists')


class MyListsView(LoginRequiredMixin, generic.ListView):
    model = List
    template_name = 'songRecommender/my_lists.html'
    context_object_name = 'moje_listy'
    paginate_by = 10

    def get_queryset(self):
        return List.objects.filter(user_id=self.request.user.pk).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MyListsView, self).get_context_data(**kwargs)
        played_songs = Played_Song.objects.all().filter(user_id=self.request.user.profile.pk)
        context['played_songs'] = played_songs.exclude(opinion=-1)[:10]
        context['nearby_songs'] = Distance_to_User.objects.all().filter(
            user_id=self.request.user.pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True))[:10]

        return context


class AllSongsView(LoginRequiredMixin, generic.ListView):
    model = Song
    template_name = 'songRecommender/all_songs.html'
    context_object_name = 'songs'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AllSongsView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)

        return context


class RecommendedSongsView(LoginRequiredMixin, generic.ListView):
    model = Distance_to_User
    template_name = 'songRecommender/recommended_songs.html'
    context_object_name = 'nearby_songs'
    paginate_by = 10

    def get_queryset(self):
        played_songs = Played_Song.objects.all().filter(user_id_id=self.request.user.profile.pk).exclude(opinion=-1)
        return Distance_to_User.objects.all().filter(
            user_id=self.request.user.pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True)
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RecommendedSongsView, self).get_context_data(**kwargs)
        context['played_songs'] = Played_Song.objects.all().filter(user_id=self.request.user.profile.pk).exclude(opinion=-1)
        # context['nearby_songs'] = Distance_to_User.objects.filter(user_id=self.request.user.profile.pk)

        return context


def likeSong(request, pk):
    played_song = Played_Song.objects.filter(song_id1_id__exact=pk, user_id=request.user.profile).get()
    if played_song.opinion != 1:
        played_song.opinion = 1

    else:
        played_song.opinion = 0
    played_song.save()

    recalculate_distances(request)

    return redirect('song_detail', request.path.split('/')[2])


def dislikeSong(request, pk):
    played_song = Played_Song.objects.filter(song_id1__exact=pk).get()
    if played_song.opinion != -1:
        played_song.opinion = -1


    else:
        played_song.opinion = 0
    played_song.save()

    recalculate_distances(request)

    return redirect('song_detail', request.path.split('/')[2])


@login_required()
def addSong(request):
    """is called when a new song is being added
    it checks if the same song is not already in the database, if not, it creates it,
    fixes the youtube link,adds it to the users played songs, and calculates the distance
     of the added song to the current user and all his lists"""

    if request.method == 'POST':
        form = SongModelForm(request.POST)
        # checks if a song with the same name and artist is already in the database
        if form.is_valid():
            song, created = Song.objects.get_or_create(song_name=form.song_name, artist=form.artist)
            # if the song was not in the database, the song will be created and added
            if created:
                song = form.save(commit=True)
                new_link = change_youtube_url(song.link)
                # changes the youtube link to an embedable format
                if new_link:
                    song.link = new_link
                    song.save()
                else:
                    form = SongModelForm()
                    return render(request, 'songRecommender/addSong.html', {'form': form})

                # calculates the distances of this song to all other songs already in the database
                TFidf_distances = get_TFidf_distance(song)
    #           W2V_distances = get_W2V_distance(song)
                # saves the distances to the database
                save_distances(TFidf_distances, song, "TF-idf")
    #            save_distances(W2V_distances, song, "W2V")

                # adds the song the user added to his played songs
                played_song = Played_Song(user_id=request.user.profile, song_id1=song, numOfTimesPlayed=1, opinion=1)
                played_song.save()

                # calculates the distance of this song to the user
                save_user_distances(song, request.user, "TF-idf")

                #  calculates the distance of this song to all of the lists the current
                # user created
                lists = List.objects.all().filter(user_id_id=request.user.id)
                for l in lists:
                    save_list_distances(song, l, request.user, "TF-idf")

                # redirects the user to his recommended songs
                return HttpResponseRedirect(reverse('recommended_songs'))

            # if the song already was in the database, it will redirect to a fail page with a link to
            # the song that potentialy collides with the new added.
            else:
                return redirect('add_song_failed', song.pk)

    else:
        form = SongModelForm()

    return render(request, 'songRecommender/addSong.html', {'form': form})


def add_song_failed(request, pk):
    """is displayed when the song that is being added is already in the database"""

    song = Song.objects.get(id=pk)

    return render(request, 'songRecommender/add_song_failed.html', {'song':song})


def signup(request):
    """is being called when a user wants to sign up
    creates a user instance in the database and sends him an email
    with confirmation information, does not send a real email yet"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # saves the user.is_active field to false, can be set to true after confirming email
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            # the email
            subject = 'Activate Your MySite Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    """is called when the user tries to confirm his email address
    if ok, it sets his profile to confirmed and redirects him to the home page
    otherwise it redirects to a activation invalid page"""
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return redirect(request, 'account_activation_invalid.html')


def account_activation_sent(request):
    """view displayed after the user hits the sign up button"""
    return render(request, 'account_activation_sent.html')


def add_song_to_list(request, pk, pk2):
    """adds song with id pk into a list with id pk2,
    firts checks if the song is not already there, if not, it adds it and
    adds it also to the users played songs if it was not already there
    then redirects to the detail page of the added song

    if the song is already there, it redirects to a fail page"""
    try:
        Song_in_List.objects.get(song_id_id=pk, list_id_id=pk2)

    except:
        song_in_list = Song_in_List(song_id_id=pk, list_id_id=pk2)
        song_in_list.save()

        check_if_in_played(pk, request.user, is_being_played=False)

        return redirect('song_detail', pk)

    return redirect('add_to_list_failed', pk, pk2)


def add_to_list_failed(request, pk, pk2):
    """fail page for when the song with id pk is already in list with id pk2"""
    song = Song.objects.get(id=pk)
    list = List.objects.get(id=pk2)

    return render(request, 'songRecommender/add_to_list_failed.html', {'song': song, 'list': list})


def logout(request):
    """is called when the user logs out"""
    logout(request)
    return render(request, 'registration/logged_out.html')


def search(request):
    """implements the search, shows ten best results if there
    are ten with a rank higher than 0, which means, if there
    are ten that are at least somewhat similar

    redirects to a search_results page with songs that were found
    the user can each song to a any of his lists"""

    vector = SearchVector('artist', 'song_name')
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        query = SearchQuery(q)

    entries = Song.objects.annotate(rank=SearchRank(vector, query)).order_by('-rank').exclude(rank=0)[:10]
    my_lists = List.objects.all().filter(user_id=request.user)

    return render(request, 'songRecommender/search_results.html', {'entries': entries, 'query': q, 'my_lists': my_lists})
