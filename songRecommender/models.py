from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm

""""""

class Song(models.Model):
    """a model representing the Song table in the database,
    stores the song name, artist, lyrics and link and also the distance to other songs"""
    song_name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    text = models.TextField()
    link = models.URLField() #default max is 200
    distance_to_other_songs = models.ManyToManyField("self", through='Distance', symmetrical=False,
                                                     related_name='songs_nearby')

    def __str__(self):
        return self.artist + ' - ' + self.song_name

    def get_distance_to_other_songs(self):
        return self.distance_to_other_songs.order_by('song_2').exclude(id=self.id)

class Profile(models.Model):
    """an one to one field to user, is created and also deleted with the user
    it has the purpose of having a many to many connection to played songs and nearby songs"""
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    played_songs = models.ManyToManyField(Song, through='Played_Song', related_name='Songs_played_by_user')
    nearby_songs = models.ManyToManyField(Song, through='Distance_to_User',related_name='Songs_close_to_user')
    email_confirmed = models.BooleanField(default=False)

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
        return self.nearby_songs.order_by('link_to_user')


class List(models.Model):
    """a model representing the list table of the database"""
    name = models.CharField(max_length=100, default='My_List')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # field with all songs that are in this list
    songs = models.ManyToManyField(Song, through='Song_in_list', related_name='songs_in_list')
    # field with songs and their distance to this list
    nearby_songs = models.ManyToManyField(Song, through='Distance_to_List', related_name='nearby_songs')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('list_detail', args=[str(self.id)])

    def get_nearby_songs(self):
        return self.nearby_songs.order_by('link_to_list')

        
class Song_in_List(models.Model):
    """class representing song_in_list table in the database
    each has a song id and a list id which together create an unique identifier
    as does an automatically generated unique object id
    the order field is not being used"""
    list_id = models.ForeignKey(List, on_delete=models.CASCADE)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(null=True)
    # for debugging reasons here
    pole_co_tu_jen_oxiduje = models.CharField(max_length=200, null=True)

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
        return reverse('song-detail', args=[str(self.song_id.id)])


class Distance(models.Model):
    """
    class representing the distance table in the database
    stores the distance between songs song_1 and song_2
    there can be more distance types added

    for each distance type there is a method to calculate the distance
    in songRecommender/Logic/Text_Shaper.py
    """
    song_1 = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='song_1')
    song_2 = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='song_2')
    distance = models.FloatField(default=0)
    DISTANCE_CHOICES = (
            ('TF-idf','TF-idf'),
            ('W2V', 'Word2Vec')
    )
    distance_Type = models.CharField(max_length=20, choices=DISTANCE_CHOICES)

    def __str__(self):
        return str(self.distance)

    class Meta:
        ordering = ['-distance']


class Distance_to_List(models.Model):
    """
    class representing the distance_to_list table in the database
    stores distance between a song and each list for every user

    there can be more distance types added
    each distance types added in the songRecommender/Logic/Text_Shaper.py
    and then used in songRecommender/Logic/model_distance_calculator.py
    in save_list_distances
    """
    list_id = models.ForeignKey(List, on_delete=models.CASCADE, null=True)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='link_to_list')
    distance = models.FloatField()
    DISTANCE_CHOICES = (
            ('TF-idf', 'TF-idf'),
            ('W2V', 'Word2Vec')
    )
    distance_Type = models.CharField(max_length= 20, choices=DISTANCE_CHOICES)

    # def get_nearby_songs(listid):
    #     nearby_songs = Distance_to_List.objects.filter(list_id=listid).order_by('-distance')[:10]
    #     return nearby_songs

    def __str__(self):
        return self.song_id.artist + ' - ' + self.song_id.song_name

    class Meta:
        ordering = ['-distance']
    

class Distance_to_User(models.Model):
    """
    class representing the distance_to_user table in the database
    stores distance between a song and all played songs for every user

    there can be more distance types added
    each distance types added in the songRecommender/Logic/Text_Shaper.py
    and then used in songRecommender/Logic/model_distance_calculator.py
    in save_user_distances
    """
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, related_name='link_to_user')
    distance = models.FloatField(default=0)
    DISTANCE_CHOICES = (
            ('TF-idf', 'TF-idf'),
            ('W2V', 'Word2Vec')
    )
    distance_Type = models.CharField(max_length=20, choices=DISTANCE_CHOICES, default='TF-idf')

    class Meta:
        ordering = ['-distance']

    # def get_nearby_songs(userid):
    #     nearby_songs = Distance_to_User.objects.filter(user_id=userid).order_by('-distance')[:10]
    #     return nearby_songs

    def __str__(self):
        return self.song_id.artist + ' - ' + self.song_id.song_name
