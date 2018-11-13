from django.views import generic
from songRecommender.models import Song, List, Song_in_List, Played_Song, Distance_to_User, Distance_to_List, Distance, Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from songRecommender.Logic.Text_Shaper import get_TFidf_distance, save_distances
# from songRecommender.Logic.Text_Shaper import get_W2V_distance
from songRecommender.Logic.model_distances_calculator import save_list_distances, save_user_distances
from songRecommender.Logic.Recommender import check_if_in_played, change_youtube_url

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token

from songRecommender.forms import SongModelForm, ListModelForm


# Create your views here.

class HomePageView(LoginRequiredMixin, generic.ListView):
    model = Distance_to_User
    context_object_name = 'home_list'
    template_name = 'songRecommender/index.html'

    def get_queryset(self):
        return Distance_to_User.objects.filter(user_id=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['my_lists'] = List.objects.filter(user_id=self.request.user)
        return context


class SongDetailView(LoginRequiredMixin, generic.DetailView):
    model = Song
    template_name = 'songRecommender/song_detail.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super(SongDetailView, self).get_context_data(**kwargs)
        context['played_song'] = Played_Song.objects.filter(song_id1=context['object'], user_id=self.request.user.profile)
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
        context['played_songs'] = Played_Song.objects.all().filter(user_id=self.request.user.pk)[:10]
        context['nearby_songs'] = Distance_to_User.objects.all().filter(user_id=self.request.user.pk)[:10]

        return context

class AllSongsView(generic.ListView):
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
        return Distance_to_User.objects.all().filter(user_id=self.request.user.pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RecommendedSongsView, self).get_context_data(**kwargs)
        context['played_songs'] = Played_Song.objects.all().filter(user_id=self.request.user.pk)
        # context['nearby_songs'] = Distance_to_User.objects.filter(user_id=self.request.user.profile.pk)

        return context


def likeSong(request, pk):
    played_song = Played_Song.objects.filter(song_id1__exact=pk).get()
    if played_song.opinion != 1:
        played_song.opinion = 1
    else:
        played_song.opinion = 0
    played_song.save()

    return redirect('song_detail', request.path.split('/')[2])


def dislikeSong(request, pk):
    played_song = Played_Song.objects.filter(song_id1__exact=pk).get()
    if played_song.opinion != -1:
        played_song.opinion = -1
    else:
        played_song.opinion = 0
    played_song.save()

    return redirect('song_detail', request.path.split('/')[2])


def addSong(request):
    if request.method == 'POST':
        form = SongModelForm(request.POST)
        if form.is_valid():
            song = form.save(commit=True)
            new_link = change_youtube_url(song.link)
            if new_link:
                song.link = new_link
                song.save()
            else:
                form = SongModelForm()
                return render(request, 'songRecommender/addSong.html', {'form': form})

            TFidf_distances = get_TFidf_distance(song)
#            W2V_distances = get_W2V_distance(song)

            save_distances(TFidf_distances, song, "TF-idf")
#            save_distances(W2V_distances, song, "W2V")

            played_song = Played_Song(user_id=request.user.profile, song_id1=song, numOfTimesPlayed=1, opinion=1)
            played_song.save()

            save_user_distances(song, request.user, "TF-idf")

            lists = List.objects.all().filter(user_id_id=request.user.id)
            for l in lists:
                save_list_distances(song, l, request.user, "TF-idf")

            return HttpResponseRedirect(reverse('recommended_songs'))

    else:
        form = SongModelForm()

    return render(request, 'songRecommender/addSong.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
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
        return render(request, 'account_activation_invalid.html')


def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')


def add_song_to_list(request, pk, pk2):
    song_in_list = Song_in_List(song_id_id=pk, list_id_id=pk2)
    song_in_list.save()

    check_if_in_played(pk, request.user.profile, is_being_played=False)

    return redirect('song_detail', pk)
