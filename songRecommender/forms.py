from django import forms
from django.contrib.auth.models import User
from .models import Profile, Song
from django.forms import ModelForm


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('played_songs', 'nearby_songs')


class SongModelForm(ModelForm):
    class Meta:
        model = Song
        fields = ['song_name', 'artist', 'text', 'link']