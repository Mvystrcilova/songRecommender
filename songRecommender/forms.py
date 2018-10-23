from django import forms
from django.contrib.auth.models import User
from .models import Profile, Song, List
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
    song_name = forms.CharField(label='',
                                widget= forms.TextInput(attrs={
                                            "class":"form-control mr-sm-2 bg-light text-white col-md-6"
                                                                }
                                                        )
                                )
    artist = forms.CharField(label='',
                                widget= forms.TextInput(attrs={
                                            "class":"form-control mr-sm-2 bg-light text-white col-md-6",
                                                                }
                                                        )
                                )
    text = forms.CharField(label='',
                           widget= forms.Textarea(attrs={
                               "class": "form-control mr-sm-2 bg-light text-white col-md-6"
                           }))
    link = forms.URLField(label='',
                          widget= forms.Textarea(attrs={
                               "class": "form-control mr-sm-2 bg-light text-white col-md-6 row-md-1"
                           }))

    class Meta:
        model = Song
        fields = ['song_name', 'artist', 'text', 'link']


class ListModelForm(ModelForm):
    class Meta:
        model = List
        fields = ['name']