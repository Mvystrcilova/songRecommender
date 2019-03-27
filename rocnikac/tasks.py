from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task

from songRecommender.models import Song, List, Played_Song, Distance, Distance_to_List, Distance_to_User, Song_in_List,\
    Profile
import pandas
from songRecommender.Logic.DocSim import DocSim
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rocnikac.settings import W2V_model, TF_

app = Celery('tasks', broker='amqp://localhost')


@shared_task
def add(x, y):
    print(x+y)
    return x + y


@shared_task
def recalculate_distances(cur_user_id, distance_type):
    """for every song in the database it recalculates
    the distance to every user and the distance to every list
    the current user has created"""

    songs = Song.objects.all()
    cur_user = Profile.objects.get(user_id__exact=cur_user_id)
    lists = List.objects.all().filter(user_id_id=cur_user_id)
    for song in songs:
        save_user_distances(song.pk, cur_user.user.pk, distance_type)

        for l in lists:
            save_list_distances(song.pk, l.pk, cur_user.user.pk, distance_type)


@shared_task
def save_user_distances(added_song_id, cur_user_id, distance_type):
    """calculates the distance of the given song to every user in database
    if the distance already exists it updates it otherwise it creates it
    the user it gets is an instance of user and NOT profile"""

    all_songs = Song.objects.all().order_by('-id')  # gets all songs from database
    cur_user = Profile.objects.get(user_id=cur_user_id)
    played_songs = Played_Song.objects.all().filter(user_id_id=cur_user.pk)  # gets all the users played songs
    added_song = Song.objects.get(pk=added_song_id)

    counter = 0
    user_to_song_distance = 0

    # for every song in the database if it is not the added song and the user played the song, it adds the distance
    # the higher the distance the closer is the song
    for song in all_songs:
        if (song.pk != added_song.pk) and (song.pk in played_songs.values_list('song_id1_id', flat=True)):

            the_song = Played_Song.objects.get(song_id1=song, user_id_id=cur_user.pk)

            if the_song.opinion != -1:
                try:
                    the_distance = Distance.objects.get(song_1=song, song_2=added_song,
                                                    distance_Type=distance_type).distance
                except:
                    the_distance = 0

                num_of_times_played = the_song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                user_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
                counter += 1

    if counter != 0:
        distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk, user_id_id=cur_user.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': user_to_song_distance / counter})
    else:
        distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk, user_id_id=cur_user.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': 0})
    distance_to_user.save()

    return


@shared_task
def save_list_distances(added_song_id, the_list_id, cur_user_id, distance_type):
    """saves the distance of given song to the given list into the database
    the cur_user it gets is and instance of user and NOT Profile"""

    all_songs = Song.objects.all().order_by('-id')
    cur_user = Profile.objects.get(user_id=cur_user_id)
    the_list = List.objects.get(pk=the_list_id)
    songs_from_list = Song_in_List.objects.filter(list_id=the_list)
    added_song = Song.objects.get(pk=added_song_id)

    counter = 0
    list_to_song_distance = 0

    # for every song in the database if it is not the added song and the list contains the song, it adds the distance
    # the higher the distance the closer is the song
    for song in all_songs:
        if (song.pk != added_song.pk) and (song.pk in songs_from_list.values_list('song_id_id', flat=True)):

            the_song = Played_Song.objects.get(song_id1=song, user_id_id=cur_user.pk)

            if the_song.opinion != -1:
                try:
                    the_distance = Distance.objects.get(song_1=song, song_2=added_song,
                                                        distance_Type=distance_type).distance
                except:
                    the_distance = 0
                num_of_times_played = the_song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                list_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
                counter += 1

    if counter != 0:
        distance_to_list, created = Distance_to_List.objects.update_or_create(song_id_id=added_song.pk,
                                                                              list_id_id=the_list.pk,
                                                                              distance_Type=distance_type,
                                                                 defaults={'distance': list_to_song_distance / counter})

    else:
        distance_to_list, created = Distance_to_List.objects.update_or_create(song_id_id=added_song.pk,
                                                                              list_id_id=the_list.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': 0})

    distance_to_list.save()

    return


@shared_task
def get_TFidf_distance():
    """gets all songs from the database except the one we are dealing with,
    computes the distances using TF-idf and saves them into a dataframe"""

    df = pandas.DataFrame(list(Song.objects.all().order_by('-id').values('text')))

    # adds the new songs lyrics to the rest of the lyrics
    songs = df['text'].tolist()

    # transforms the dataset into a matrix
    tfidf_vectorizer = TfidfVectorizer()


    tfidf_matrix_train = tfidf_vectorizer.fit_transform(songs)  # finds the tfidf score with normalization

    return cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)[0]


@shared_task
def save_distances(distances, addedSong_id, dist_Type):
    """gets all the distances as attributes,
    finds all songs in database and stores new objects of the Distance
    into the Distance Table"""

    all_songs = Song.objects.all().order_by('-id')
    addedSong = Song.objects.get(pk=addedSong_id)
    counter = 0
    # for every song it gets its data and added songs data and saves distance
    for song in all_songs:
        if song.pk != addedSong_id: #checks if the processed and added song are not the same
            dist_1 = Distance(song_1=song, song_2=addedSong, distance=distances[counter], distance_Type=dist_Type)
            dist_2 = Distance(song_1=addedSong, song_2=song, distance=distances[counter], distance_Type=dist_Type)
            dist_1.save()
            dist_2.save()
        counter += 1
    return


@shared_task()
def get_W2V_distance(addedSong_id):
    """gets all songs from the database except the one we are dealing with,
    computes the distances using W2V and saves them into a dataframe"""
    ds = DocSim(W2V_model)
    df = pandas.DataFrame(list(Song.objects.all().order_by('-id').values('text')))
    addedSong = Song.objects.get(pk=addedSong_id)
    # adds the new songs lyrics to the rest of the lyrics
    songs = df['text'].tolist()

    return ds.calculate_similarity(addedSong.text, songs)

@shared_task()
def handle_added_song(song_id, user_id):
    # calculates the distances of this song to all other songs already in the database
    song = Song.objects.get(pk=song_id)
    TFidf_distances = get_TFidf_distance()

    W2V_distances = get_W2V_distance(song_id)

    # saves the distances to the database
    save_distances(TFidf_distances, song_id, "TF-idf")
    save_distances(W2V_distances, song_id, "W2V")

    # calculates the distance of this song to the user
    save_user_distances(song_id, user_id, "TF-idf")
    save_user_distances(song_id, user_id, "W2V")

    #  calculates the distance of this song to all of the lists the current
    # user created
    lists = List.objects.all().filter(user_id_id=user_id)
    for l in lists:
        save_list_distances(song_id, l.pk, user_id, "TF-idf")
        save_list_distances(song_id, l.pk, user_id, "W2V")