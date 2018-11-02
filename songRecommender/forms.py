from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Song, List, Played_Song
from django.forms import ModelForm


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('played_songs', 'nearby_songs')

class PlayedModelFrom(ModelForm):
    class Meta:
        model = Played_Song
        fields = ['user_id', 'song_id1', 'numOfTimesPlayed', 'opinion']


class SongModelForm(ModelForm):
    song_name = forms.CharField(label='',
                                widget=forms.TextInput(attrs={
                                    "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6"
                                }
                                )
                                )
    artist = forms.CharField(label='',
                             widget=forms.TextInput(attrs={
                                 "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6",
                             }
                             )
                             )
    text = forms.CharField(label='',
                           widget=forms.Textarea(attrs={
                               "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6"
                           }))
    link = forms.URLField(label='',
                          widget=forms.TextInput(attrs={
                              "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6"
                          }))

    class Meta:
        model = Song
        fields = ['song_name', 'artist', 'text', 'link']


class ListModelForm(ModelForm):
    name = forms.CharField(label='',
                           widget=forms.TextInput(attrs={
                               "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6"
                           }
                           )
                           )

    class Meta:
        model = List
        fields = ['name']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
