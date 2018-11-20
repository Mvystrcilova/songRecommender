from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Song, List, Played_Song
from django.forms import ModelForm


class SongModelForm(ModelForm):
    """form that allows the user to add a new song into the database"""
    song_name = forms.CharField(label='',
                                widget=forms.TextInput(attrs={
                                    "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6"
                                }))
    artist = forms.CharField(label='',
                             widget=forms.TextInput(attrs={
                                 "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6",
                             }))
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

    def clean(self):

        return


class ListModelForm(ModelForm):
    """a form that allows the user to create a list"""

    name = forms.CharField(label='',
                           widget=forms.TextInput(attrs={
                               "class": "form-control mr-sm-2 bg-light text-lightgray col-md-6"
                           }))

    class Meta:
        model = List
        fields = ['name']


class SignUpForm(UserCreationForm):
    """a form that allows a not-yet user to create an account"""
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


