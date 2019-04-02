from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task

from songRecommender.models import Song, List, Played_Song, Distance, Distance_to_List, Distance_to_User, Song_in_List,\
    Profile
import pandas, sklearn
from songRecommender.Logic.DocSim import DocSim
from songRecommender.Logic.adding_songs import save_all_representations_and_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rocnikac.settings import W2V_model, TF_idf_model
from keras.models import model_from_json
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

    cur_user = Profile.objects.get(user_id=cur_user_id)
    played_songs = Played_Song.objects.all().filter(user_id_id=cur_user.pk)  # gets all the users played songs
    added_song = Song.objects.get(pk=added_song_id)

    counter = 0
    user_to_song_distance = 0

    # for every song in the database if it is not the added song and the user played the song, it adds the distance
    # the higher the distance the closer is the song
    for song in played_songs:
        if song.song_id1.pk != added_song.pk:

            if song.opinion != -1:
                try:
                    the_distance = Distance.objects.get(song_1=song.song_id1, song_2=added_song,
                                                    distance_Type=distance_type).distance
                except:
                    the_distance = 0

                num_of_times_played = song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                user_to_song_distance += the_distance * num_of_times_played + the_distance * song.opinion
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

    cur_user = Profile.objects.get(user_id=cur_user_id)
    the_list = List.objects.get(pk=the_list_id)
    songs_from_list = Song_in_List.objects.filter(list_id=the_list)
    added_song = Song.objects.get(pk=added_song_id)

    counter = 0
    list_to_song_distance = 0

    # for every song in the database if it is not the added song and the list contains the song, it adds the distance
    # the higher the distance the closer is the song
    for song in songs_from_list:
        if song.song_id.pk != added_song.pk:

            the_song = Played_Song.objects.get(song_id1=song.song_id, user_id_id=cur_user.pk)

            if the_song.opinion != -1:
                try:
                    the_distance = Distance.objects.get(song_1=song.song_id, song_2=added_song,
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

@shared_task()
def handle_added_song(song_id, user_id):
    # calculates the distances of this song to all other songs already in the database
    song = Song.objects.get(pk=song_id)

    # TFidf_distances = get_TFidf_distance()
    #
    # W2V_distances = get_W2V_distance(song_id)
    #
    # # saves the distances to the database
    # save_distances(TFidf_distances, song_id, "TF-idf")
    # save_distances(W2V_distances, song_id, "W2V")
    # json_file = open('rocnikac/models/GRU_Mel_model.json', 'r')
    # loaded_model_json = json_file.read()
    # json_file.close()
    # GRU_Mel_model = model_from_json(loaded_model_json)
    # # load weights into new model
    # GRU_Mel_model.load_weights("rocnikac/models/GRU_Mel_model.h5")
    # print("Loaded model from disk")
    #
    # json_file = open('rocnikac/models/LSTM_Mel_model.json', 'r')
    # loaded_model_json = json_file.read()
    # json_file.close()
    # LSTM_Mel_model = model_from_json(loaded_model_json)
    # # load weights into new model
    # LSTM_Mel_model.load_weights("rocnikac/models/LSTM_Mel_model.h5")
    # print("Loaded model from disk")

    save_all_representations_and_distances(song_id)
    # calculates the distance of this song to the user
    save_user_distances(song_id, user_id, "TF-idf")
    save_user_distances(song_id, user_id, "W2V")
    save_user_distances(song_id, user_id, "MFCC")
    save_user_distances(song_id, user_id, "PCA_SPEC")
    save_user_distances(song_id, user_id, "PCA_MEL")
    save_user_distances(song_id, user_id, "GRU_MEL")
    save_user_distances(song_id, user_id, "GRU_SPEC")
    save_user_distances(song_id, user_id, "LSTM_MEL")
    #  calculates the distance of this song to all of the lists the current
    # user created
    lists = List.objects.all().filter(user_id_id=user_id)
    for l in lists:
        save_list_distances(song_id, l.pk, user_id, "TF-idf")
        save_list_distances(song_id, l.pk, user_id, "W2V")
        save_list_distances(song_id, l.pk, user_id, "MFCC")
        save_list_distances(song_id, l.pk, user_id, "PCA_SPEC")
        save_list_distances(song_id, l.pk, user_id, "PCA_MEL")
        save_list_distances(song_id, l.pk, user_id, "GRU_MEL")
        save_list_distances(song_id, l.pk, user_id, "GRU_SPEC")
        save_list_distances(song_id, l.pk, user_id, "LSTM_MEL")