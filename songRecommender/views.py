from django.views import generic
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template.loader import render_to_string
from django.views.generic.list import MultipleObjectMixin

from songRecommender.data.load_distances import load_songs_to_database, load_all_representations, load_all_distances
from songRecommender.forms import SongModelForm, ListModelForm
from songRecommender.models import Song, List, Song_in_List, Played_Song, Distance_to_User, Distance, Distance_to_List
from songRecommender_project.tasks import handle_added_song, recalculate_distanced_when_new_song_added, recalculate_all_distances_to_user, recalculate_all_distances_to_list, recalculate_distances_for_relevant_lists
from songRecommender.Logic.Recommender import check_if_in_played
from songRecommender_project.settings import EMAIL_DISABLED
from .forms import SignUpForm
from .tokens import account_activation_token

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
"""this module contains all the view in the application"""


class HomePageView(LoginRequiredMixin, generic.ListView):
    """class showing the home page
    shows his lists and recommended songs to the user

    Overridden methods:
    ------------------
    get_queryset()
        :returns all songs the user has not played yet but with respect
        to their distance to the user

    get_context_data()
        besides the queryset specified in get_queryset() it adds the users
        lists to the context and returns the updated context
    """

    model = Distance_to_User
    context_object_name = 'home_list'
    template_name = 'songRecommender/index.html'

    def get_queryset(self):
        """:returns all songs the user has not played yet but with respect
        to their distance to the user """
        played_songs = Played_Song.objects.all().filter(user_id=self.request.user.profile.pk)
        return Distance_to_User.objects.all().filter(
            distance_Type=self.request.user.profile.user_selected_distance_type,
            user_id=self.request.user.pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True)).order_by('-distance')

    def get_context_data(self, **kwargs):
        """:returns the queryset with the current users lists included"""
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)
        return context


class SongDetailView(LoginRequiredMixin, generic.DetailView):
    """class creating a detail view for each song

    Overridden Methods
    -----------------
    get_context_data()
        besides the song it also checks if the song the user is accessing was
        viewed before, if not, it is added to the played songs

        then the played song with this song and the current user is passed
        and all the current users lists
    """
    model = Song
    template_name = 'songRecommender/song_detail.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        """function that returns the context for the html page,
        has the same parameters as base function

        additionally checks if the song the user is viewing is already in his played
        songs, if not it adds it

        the context provided, besides the song specified by an unique id
        is also the played song corresponding to the song from the detail view and
        all the lists created by the current user

        There is the possibility to store data inside the database when uncommenting the designated lines inside
        of this function
        """
        #### section to be run when loaded data into the database #####

        # NOTE!!! It is necessary to have the songs loaded inside the dabase using "load_songs_to_database()" BEFORE
        # loading the representations and distances

        # For loading uncomment the next three lines:
        # load_songs_to_database()
        # load_all_representations()
        # load_all_distances()
        context = super(SongDetailView, self).get_context_data(**kwargs)
        check_if_in_played(context['object'].pk, self.request.user, is_being_played=True)

        played_songs = Played_Song.objects.filter(user_id=self.request.user.profile.pk)
        context['played_song'] = Played_Song.objects.filter(
            song_id1=context['object'], user_id=self.request.user.profile)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)
        #POZOR!!! Napraseni kod, co ale funguje, mozna potom prejmenovat, vraci se distance ale pouziva song
        context['nearby_songs'] = Distance.objects.filter(
            distance_Type=self.request.user.profile.user_selected_distance_type, song_2=context['object']).exclude(
            song_1_id__in=played_songs.values_list('song_id1_id', flat=True).order_by('-distance'))[:10]
        context['link'] = context['object'].link_on_disc
        return context


class ListDetailView(LoginRequiredMixin, generic.DetailView, MultipleObjectMixin):
    """class generating a detail view for a particular list

    Overridden Methods
    -----------------
    get_gueryset()
        :returns all lists created by the current user, not just
        the one in the view
    """
    model = List
    template_name = 'songRecommender/list_detail.html'
    paginate_by = 10
    page = 1

    def get_queryset(self):
        return List.objects.filter(user_id=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        songs = Song_in_List.objects.filter(list_id=self.get_object().pk)
        context = super(ListDetailView, self).get_context_data(object_list=songs, **kwargs)
        played_songs = Played_Song.objects.filter(user_id=self.request.user.profile.pk)
        context['songs'] = songs
        context['nearby_songs'] = Distance_to_List.objects.filter(
            distance_Type=self.request.user.profile.user_selected_distance_type,
            list_id=context['object'].pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True)).order_by('-distance')[:10]
        context['start_page'] = context['page_obj'].number - 3
        context['end_page'] = context['page_obj'].number + 3
        return context

class ListCreate(LoginRequiredMixin, CreateView):
    """ class representing a create view, which means a form
    for a list

    Overridden Methods
    -----------------

    post()
        since the user does not fill the user_id field
        after submiting the form, the user_id is added to the list
        and saved afterwards
    """

    model = List
    fields = ['name']

    def post(self, request, *args, **kwargs):
        """overrides the base post method
        adds the current user id to the lists user_id field
        in table"""
        form = ListModelForm(data=request.POST)
        if form.is_valid():
            _list = form.save(commit=False)
            _list.user_id = request.user
            _list.save()
        return HttpResponseRedirect(reverse('index'))


class ListUpdate(LoginRequiredMixin, UpdateView):
    """build in django view for updating an instance of a model in the database,
     in this case a list"""
    model = List
    # fields = ['name']


class ListDelete(LoginRequiredMixin, DeleteView):
    """build in django view for deleting an instance of a model
    from the database, in this case a list"""
    model = List
    success_url = reverse_lazy('my_lists')


class MyListsView(LoginRequiredMixin, generic.ListView):
    """a class based django view, displays the current users list with songs
    most similar to those in each list

    Overridden methods
    ------------------
    get_queryset(self)
        :returns not all lists but only lists created by this user

    get_context_data()
        has same attributes as base method
        besides the list of the current user, it adds his played sons, but hides those
        he disliked, and it also adds the songs most recommended for this user except of
        those he already played

    """
    model = List
    template_name = 'songRecommender/my_lists.html'
    context_object_name = 'moje_listy'


    def get_queryset(self):
        return List.objects.filter(user_id=self.request.user.pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MyListsView, self).get_context_data(**kwargs)
        played_songs = Played_Song.objects.filter(user_id=self.request.user.profile.pk)
        context['played_songs'] = played_songs.exclude(opinion=-1)
        #!!! POZOR napraseny kod, vracime Distance to user ale pouziva se song
        context['recommended_songs'] = Distance_to_User.objects.all().filter(
            distance_Type=self.request.user.profile.user_selected_distance_type,
            user_id=self.request.user.pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True).order_by('-distance'))[:10]

        return context


class AllSongsView(LoginRequiredMixin, generic.ListView):
    """ class based django view that shows all songs stored in the database
    in a not specified order to every user in the same way
    the only difference is that every user can add those songs to only his own list

    Overridden methods
    ------------------

    get_context_data()
        attributes are the same as base method
        besides all song objects it also return all lists that belong
        to the current user

    """
    model = Song
    template_name = 'songRecommender/all_songs.html'
    context_object_name = 'songs'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        """attributes are the same as base method
        besides all song objects it also return all lists that belong
        to the current user"""

        context = super(AllSongsView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)
        context['start_page'] = context['page_obj'].number - 3
        context['end_page'] = context['page_obj'].number + 3

        return context


class RecommendedSongsView(LoginRequiredMixin, generic.ListView):
    """
    class used for the recommended songs page
    displays songs the user played and did not dislike and the songs that are
    recommended to him based on all played songs

    Overridden Methods
    -----------------

    get_query_set(self)
        :returns only the songs recommended to the user that he did not played
        before

    get_context_data
        :returns the songs recommended based on get_query_set and adds
        played songs except of those the user disliked to be shown in this
        view
    """

    model = Played_Song
    template_name = 'songRecommender/recommended_songs.html'
    context_object_name = 'played_songs'
    paginate_by = 10

    def get_queryset(self):
        """:returns only the songs recommended to the user that he did not played
        before from the table distance_to_user"""
        return Played_Song.objects.filter(user_id_id=self.request.user.profile.pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        :returns the songs recommended based on get_query_set and adds
        played songs except of those the user disliked to be shown in this
        view
        """
        context = super(RecommendedSongsView, self).get_context_data(**kwargs)
        played_songs = Played_Song.objects.filter(
            user_id=self.request.user.profile.pk)
        context['nearby_songs'] = (Distance_to_User.objects.all().filter(
            distance_Type=self.request.user.profile.user_selected_distance_type,
            user_id=self.request.user.pk).exclude(
            song_id_id__in=played_songs.values_list('song_id1_id', flat=True)).order_by('-distance'))[:10]

        context['start_page'] = context['page_obj'].number - 4
        context['end_page'] = context['page_obj'].number + 4

        return context


def likeSong(request, pk):
    """
    this function based view is called when a user likes a song or unlikes a liked song
    liking a song results into recalculating distances to the user and to
    all lists with recalculate distances

    :param request: the http request
    :param pk: the id of the song the user liked
    :return: redirects to the detail page of the song the user liked
    """
    played_song = Played_Song.objects.filter(song_id1_id__exact=pk, user_id=request.user.profile).get()
    # if song was not liked before it is liked
    if played_song.opinion != 1:
        played_song.opinion = 1

    # if song was liked before it is unliked but NOT disliked
    else:
        played_song.opinion = 0
    played_song.save()

    # recalculates the distance of all songs to the user and his lists based
    user_id = int(request.user.id)
    recalculate_all_distances_to_user.delay(pk, user_id)
    recalculate_distances_for_relevant_lists.delay(pk, user_id)

    return redirect('song_detail', request.path.split('/')[2])


def dislikeSong(request, pk):
    """
    this function based view is called when a user dislikes a song or undisikes a liked song
    liking a song results into recalculating distances to the user and to
    all lists with recalculate distances

    :param request: the http reques
    :param pk: id of the song the user disliked or undisliked
    :return: redirects to the detail page of the disliked or undisliked song
    """
    played_song = Played_Song.objects.filter(song_id1__exact=pk, user_id=request.user.profile).get()
    # if song was not disliked before it is now
    if played_song.opinion != -1:
        played_song.opinion = -1
    # if song was disliked before it is now not liked neither disliked
    else:
        played_song.opinion = 0
    played_song.save()

    # recalculates the distances of all songs to the user and all his lists
    user_id = request.user.pk
    recalculate_all_distances_to_user.delay(pk, user_id)

    return redirect('song_detail', request.path.split('/')[2])


@login_required()
def addSong(request):
    """is called when a new song is being added
    it checks if the same song is not already in the database, if not, it creates it,
    fixes the youtube link,adds it to the users played songs, and calculates the distance
     of the added song to the current user and all his lists
     """

    if request.method == 'POST':
        form = SongModelForm(request.POST)
        # checks if a song with the same name and artist is already in the database
        if form.is_valid():
            song, created = Song.objects.get_or_create(song_name=form.cleaned_data['song_name'],
                                                       artist=form.cleaned_data['artist'])
            # if the song was not in the database, the song will be created and added
            if created:
                song.text = form.cleaned_data['text']
                song.link = form.cleaned_data['link']
                # new_link = change_youtube_url(song.link)
                # changes the youtube link to an embedable format
                # if new_link:
                #     song.link = new_link
                song.save()
                # else:
                #     form = SongModelForm()
                #     return render(request, 'songRecommender/addSong.html', {'form': form})

                # adds the song the user added to his played songs
                played_song, created = Played_Song.objects.get_or_create(user_id=request.user.profile, song_id1=song, numOfTimesPlayed=1, opinion=1)
                if created:
                    played_song.save()

                handle_added_song(song.pk)
                recalculate_distanced_when_new_song_added.delay(song.pk)


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
            user.is_active = EMAIL_DISABLED
            user.save()
            if not EMAIL_DISABLED:
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
                return redirect('index')
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
        recalculate_all_distances_to_list.delay(pk, pk2)

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
    my_lists = List.objects.all().filter(user_id=request.user)
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        query = SearchQuery(q)

        entries = Song.objects.annotate(rank=SearchRank(vector, query)).order_by('-rank').exclude(rank=0)[:10]


        return render(request, 'songRecommender/search_results.html', {'entries': entries, 'query': q, 'my_lists': my_lists})

    return render(request, 'songRecommender/search_results.html', {'entries': {}, 'query': {}, 'my_lists': my_lists })


def change_distance(request):
    """
    Changes the distance based on which the recommendations are calculated
    :param request: the HTML request
    :return: Redirects to the same page
    """
    next_page = request.GET.get('next')
    user = request.user
    if 'PCA_TF-idf' in request.GET:
        user.profile.user_selected_distance_type = "PCA_TF-idf"
    elif 'W2V' in request.GET:
        user.profile.user_selected_distance_type = "W2V"
    elif 'PCA_MEL' in request.GET:
        user.profile.user_selected_distance_type = "PCA_MEL"
    elif 'LSTM_MFCC' in request.GET:
        user.profile.user_selected_distance_type = "LSTM_MFCC"
    elif 'GRU_MEL' in request.GET:
        user.profile.user_selected_distance_type = "GRU_MEL"

    user.profile.save()

    return HttpResponseRedirect(next_page)


def delete_account(request):
    user = request.user
    user.profile.delete()
    user.delete()

    return render(request, 'registration/logged_out.html')


def get_about(request):

    return render(request, 'songRecommender/about.html')

