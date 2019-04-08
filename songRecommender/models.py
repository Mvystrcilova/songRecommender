from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from rocnikac.settings import EMAIL_DISABLED, SELECTED_DISTANCE_TYPE

import numpy

class Song(models.Model):
    """a model representing the Song table in the database,
    stores the song name, artist, lyrics and link and also the distance to other songs"""
    song_name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    text = models.TextField()
    link = models.URLField(max_length=1000) #default max is 200
    distance_to_other_songs = models.ManyToManyField("self", through='Distance', symmetrical=False,
                                                     related_name='songs_nearby')
    link_on_disc = models.FileField(blank=True,null=True, max_length=500, upload_to='mp3_files/')
    tf_idf_representation = ArrayField(models.FloatField(blank=True), null=True)
    w2v_representation = ArrayField(models.FloatField(blank=True), null=True)
    spectrogram_representation = ArrayField(ArrayField(models.FloatField(blank=True)), null=True)
    mel_spectrogram_representation = ArrayField(ArrayField(models.FloatField(blank=True)), null=True)
    mfcc_representation = ArrayField(ArrayField(models.FloatField(blank=True)), null=True)
    pca_spec_representation = ArrayField(models.FloatField(blank=True), null=True)
    pca_mel_representation = ArrayField(models.FloatField(blank=True), null=True)
    gru_mel_representation = ArrayField(ArrayField(models.FloatField(blank=True)), null=True)
    lstm_spec_representation = ArrayField(ArrayField(models.FloatField(blank=True)), null=True)
    lstm_mel_representation = ArrayField(ArrayField(models.FloatField(blank=True)), null=True)

    def get_tf_idf_representation(self):
        pass

    def get_W2V_representation(self):
        pass

    def get_spectrogram_representation(self):
        return numpy.load(self.spectrogram_representation)

    def get_mel_spectrogram_representation(self):
        return numpy.load(self.mel_spectrogram_representation)

    def get_mfcc_representation(self):
        return numpy.load(self.mfcc_representation)

    def get_pca_spec_representation(self):
        return numpy.load(self.pca_spec_representation)

    def get_pca_mel_representation(self):
        return numpy.load(self.pca_mel_representation)

    def get_gru_mel_representation(self):
        return numpy.load(self.gru_mel_representation)

    def get_lstm_spec_representatio(self):
        return numpy.load(self.gru_spec_representation)

    def get_lstm_mel_representation(self):
        return numpy.load(self.lstm_mel_representation)


    def __str__(self):
        return self.artist + ' - ' + self.song_name

    def get_distance_to_other_songs(self):
        return self.distance_to_other_songs.filter(song_2__distance_Type=SELECTED_DISTANCE_TYPE).order_by(
            'song_2').exclude(id=self.id)



class Profile(models.Model):
    """an one to one field to user, is created and also deleted with the user
    it has the purpose of having a many to many connection to played songs and nearby songs"""
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    played_songs = models.ManyToManyField(Song, through='Played_Song', related_name='Songs_played_by_user')
    nearby_songs = models.ManyToManyField(Song, through='Distance_to_User',related_name='Songs_close_to_user')
    email_confirmed = models.BooleanField(default=EMAIL_DISABLED)
    DISTANCE_CHOICES = (
        ('TF-idf', 'TF-idf'),
        ('W2V', 'Word2Vec'),
        ('MFCC', 'Mel-frequency cepstral coefficients'),
        ('PCA_SPEC', 'PCA on spectrograms'),
        ('MEL_SPEC', 'PCA on mel-spectrograms'),
        ('GRU_MEL', 'GRU neural network with mel-spectrogram input'),
        ('GRU_SPEC', 'GRU autoencoder with spectrogram input'),
        ('LSTM_MEL', 'LSTM autoencoder with mel-spectrogram input')
    )
    user_selected_distance_type = models.CharField(max_length=20, choices=DISTANCE_CHOICES,
                                                   default=SELECTED_DISTANCE_TYPE)


    def get_object(self):
        return self.request.user

    def __str__(self):
        return self.request.user.username

    def get_profile(self):
        return self

    def update_profile(request, user_id):
        """if the profile is updated, the user is updated too"""
        user = User.objects.get(pk=user_id)
        user.save()

    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        """when the user is created or updated the profile is created or updated as well"""
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()

    def get_nearby_songs(self):
        return self.nearby_songs.filter(
            Distance_to_User__distance_Type=SELECTED_DISTANCE_TYPE).order_by('link_to_user')


class List(models.Model):
    """a model representing the list table of the database"""
    name = models.CharField(max_length=100, default='My_List')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # field with all songs that are in this list
    songs = models.ManyToManyField(Song, through='Song_in_List', related_name='songs_in_list')
    # field with songs and their distance to this list
    nearby_songs = models.ManyToManyField(Song, through='Distance_to_List', related_name='nearby_songs')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('list_detail', args=[str(self.id)])

    def get_nearby_songs(self):
        list_user = Profile.objects.get(user_id=self.user_id)
        played_songs = Played_Song.objects.all().filter(user_id=list_user.pk)

        nearby_songs = Distance_to_List.objects.filter(distance_Type=list_user.user_selected_distance_type
                                                       ).exclude(song_id_id__in=played_songs.values_list('song_id1_id', flat=True))
        return nearby_songs
            # self.nearby_songs.exclude(Distance_to_List__song_id__in=self.songs.values_list(
            # 'song_id_id', flat=True)).order_by('-link_to_list')[:10]


class Song_in_List(models.Model):
    """class representing song_in_list table in the database
    each has a song id and a list id which together create an unique identifier
    as does an automatically generated unique object id
    the order field is not being used"""
    list_id = models.ForeignKey(List, on_delete=models.CASCADE)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(null=True)
    # for debugging reasons here

    class Meta:
        ordering = ['-order']

    def __str__(self):
        return self.song_id.song_name

    def get_absolute_url(self):
        return reverse('song_detail', args=[str(self.song_id.id)])


class Played_Song(models.Model):
    """class representing a played song
    for each song, there should be only one played song for each user
    meaning, the user_id and the song_id create an unique identifier
    """
    song_id1 = models.ForeignKey(Song, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    numOfTimesPlayed = models.PositiveIntegerField(default=1)
    OPINION_CHOICES = (
            (1, 'Like'),
            (0, 'No opinion'),
            (2, 'Dislike'),
    )
    opinion = models.IntegerField(choices=OPINION_CHOICES, default=0)


    def __str__(self):
        return self.song_id1.song_name

    def get_absolute_url(self):
        return reverse('song-detail', args=[str(self.song_id1.id)])

    class Meta:
        unique_together = (('song_id1', 'user_id'))

class Distance(models.Model):
    """
    class representing the distance table in the database
    stores the distance between songs song_1 and song_2
    there can be more distance types added

    for each distance type there is a method to calculate the distance
    in rocnikac/tasks.py
    """
    song_1 = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='song_1')
    song_2 = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='song_2')
    distance = models.FloatField(default=0)
    DISTANCE_CHOICES = (
            ('TF-idf','TF-idf'),
            ('W2V', 'Word2Vec'),
            ('MFCC', 'Mel-frequency cepstral coefficients'),
            ('PCA_SPEC', 'PCA on spectrograms'),
            ('PCA_MEL', 'PCA on mel-spectrograms'),
            ('GRU_MEL', 'GRU neural network with mel-spectrogram input'),
            ('GRU_SPEC', 'GRU autoencoder with spectrogram input'),
            ('LSTM_MEL', 'LSTM autoencoder with mel-spectrogram input')
    )
    distance_Type = models.CharField(max_length=20, choices=DISTANCE_CHOICES)

    def __str__(self):
        return str(self.song_1.artist) + " - " + str(self.song_1.song_name)

    class Meta:
        ordering = ['-distance']
        unique_together = (('song_1', 'song_2'))


class Distance_to_List(models.Model):
    """
    class representing the distance_to_list table in the database
    stores distance between a song and each list for every user

    there can be more distance types added
    each distance types added in the rocnikac/tasks.py
    and then used in rocnikac/tasks.py
    in save_list_distances
    """
    list_id = models.ForeignKey(List, on_delete=models.CASCADE, null=True)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='link_to_list')
    distance = models.FloatField()
    DISTANCE_CHOICES = (
            ('TF-idf', 'TF-idf'),
            ('W2V', 'Word2Vec'),
            ('MFCC', 'Mel-frequency cepstral coefficients'),
            ('PCA_SPEC', 'PCA on spectrograms'),
            ('PCA_MEL', 'PCA on mel-spectrograms'),
            ('GRU_MEL', 'GRU neural network with mel-spectrogram input'),
            ('GRU_SPEC', 'GRU autoencoder with spectrogram input'),
            ('LSTM_MEL', 'LSTM autoencoder with mel-spectrogram input')
    )
    distance_Type = models.CharField(max_length= 20, choices=DISTANCE_CHOICES)

    # def get_nearby_songs(listid):
    #     nearby_songs = Distance_to_List.objects.filter(list_id=listid).order_by('-distance')[:10]
    #     return nearby_songs

    def __str__(self):
        return self.song_id.artist + ' - ' + self.song_id.song_name

    class Meta:
        ordering = ['-distance']
        unique_together=(('list_id', 'song_id'))
    

class Distance_to_User(models.Model):
    """
    class representing the distance_to_user table in the database
    stores distance between a song and all played songs for every user

    there can be more distance types added
    each distance types added in the rocnikac/tasks.py
    and then used in songRecommender/Logic/model_distance_calculator.py
    in save_user_distances
    """
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='link_to_user')
    distance = models.FloatField(default=0)
    DISTANCE_CHOICES = (
            ('TF-idf', 'TF-idf'),
            ('W2V', 'Word2Vec'),
            ('MFCC', 'Mel-frequency cepstral coefficients'),
            ('PCA_SPEC', 'PCA on spectrograms'),
            ('PCA_MEL', 'PCA on mel-spectrograms'),
            ('GRU_MEL', 'GRU neural network with mel-spectrogram input'),
            ('GRU_SPEC', 'GRU autoencoder with spectrogram input'),
            ('LSTM_MEL', 'LSTM autoencoder with mel-spectrogram input')
    )
    distance_Type = models.CharField(max_length=20, choices=DISTANCE_CHOICES, default='TF-idf')

    class Meta:
        ordering = ['-distance']
        unique_together=(('user_id', 'song_id'))

    # def get_nearby_songs(userid):
    #     nearby_songs = Distance_to_User.objects.filter(user_id=userid).order_by('-distance')[:10]
    #     return nearby_songs

    def __str__(self):
        return self.song_id.artist + ' - ' + self.song_id.song_name
