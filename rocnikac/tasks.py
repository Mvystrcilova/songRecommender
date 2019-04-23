from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task

import math
from songRecommender.models import Song, List, Played_Song, Distance, Distance_to_List, Distance_to_User, Song_in_List,\
    Profile
import pandas, sklearn, numpy
from django.db.models import Sum, Count, Avg
from songRecommender.Logic.DocSim import DocSim
from songRecommender.Logic.adding_songs import save_all_representations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rocnikac.settings import W2V_model, TF_idf_model
from keras.models import model_from_json

from rocnikac.settings import PCA_TF_IDF_THRESHOLD, W2V_THRESHOLD, LSTM_MFCC_THRESHOLD, PCA_MEL_THRESHOLD, GRU_MEL_THRESHOLD

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


    songs = Song.objects.all().only('id')
    cur_user = Profile.objects.get(user_id__exact=cur_user_id)
    lists = List.objects.all().filter(user_id_id=cur_user_id)
    for song in songs:
        save_user_distances(song.pk, cur_user.user.pk, distance_type)

        for l in lists:
            save_list_distances(song.pk, l.pk, cur_user.user.pk, distance_type)

@shared_task
def recalculate_all_distances(cur_user_id):
    # recalculate_distances(cur_user_id, 'PCA_Tf-idf')
    recalculate_distances(cur_user_id, 'W2V')
    recalculate_distances(cur_user_id, 'PCA_MEL')
    recalculate_distances(cur_user_id, 'GRU_MEL')
    recalculate_distances(cur_user_id, 'LSTM_MFCC')
@shared_task
def save_user_distances(added_song_id, cur_user_id, distance_type):
    """calculates the distance of the given song to every user in database
    if the distance already exists it updates it otherwise it creates it
    the user it gets is an instance of user and NOT profile"""

    cur_user = Profile.objects.get(user_id=cur_user_id)
    played_songs = Played_Song.objects.all().filter(user_id_id=cur_user.pk).exclude(opinion=-1)
    added_song = Song.objects.get(pk=added_song_id)

    # counter = 0
    # user_to_song_distance = 0
    distances = Distance.objects.filter(song_1_id=added_song_id, song_2_id__in=played_songs.values_list('song_id1', flat=True), distance_Type=distance_type
                                              ).aggregate(total=Avg('distance'))['total']
    liked_distances = Distance.objects.filter(song_1_id=added_song_id, song_2_id__in=played_songs.exclude(opinion=0).values_list('song_id1', flat=True), distance_Type=distance_type
                                                    ).aggregate(total=Avg('distance'))['total']
    if (distances is not None) and (liked_distances is not None):
        final_distance = distances + liked_distances
        distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk,
                                                                              user_id_id=cur_user.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': final_distance})
        distance_to_user.save()
    elif distances is not None:
        distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk,
                                                                              user_id_id=cur_user.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': distances})
        distance_to_user.save()


    # for every song in the database if it is not the added song and the user played the song, it adds the distance
    # the higher the distance the closer is the song
    # for song in played_songs:
    #
    #     if song.song_id1.pk != added_song.pk:
    #
    #         if song.opinion != -1:
    #             try:
    #                 the_distance = Distance.objects.get(song_1=song.song_id1, song_2=added_song,
    #                                                 distance_Type=distance_type).distance
    #             except:
    #                 the_distance = 0
    #
    #             num_of_times_played = song.numOfTimesPlayed
    #
    #             # the distance is multiplied by the number of times the user played the song
    #             # also if the user likes the song, one more distance is added, if he does not the second part is 0
    #             user_to_song_distance += the_distance * num_of_times_played + the_distance * song.opinion
    #             counter += 1
    #
    # if counter != 0:
    #     distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk, user_id_id=cur_user.pk,
    #                                                                           distance_Type=distance_type,
    #                                                                           defaults={'distance': user_to_song_distance / counter})
    # else:


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

    distances = Distance.objects.all().filter(song_1_id=added_song_id,
                                              song_2_id__in=songs_from_list.values_list('song_id_id', flat=True),
                                              distance_Type=distance_type).aggregate(total=Avg('distance'))['total']



    # for every song in the database if it is not the added song and the list contains the song, it adds the distance
    # the higher the distance the closer is the song
    # for song in songs_from_list:
    #     if song.song_id.pk != added_song.pk:
    #
    #         the_song = Played_Song.objects.get(song_id1=song.song_id, user_id_id=cur_user.pk)
    #
    #         if the_song.opinion != -1:
    #             try:
    #                 the_distance = Distance.objects.get(song_1=song.song_id, song_2=added_song,
    #                                                     distance_Type=distance_type).distance
    #             except:
    #                 the_distance = 0
    #             num_of_times_played = the_song.numOfTimesPlayed
    #
    #             # the distance is multiplied by the number of times the user played the song
    #             # also if the user likes the song, one more distance is added, if he does not the second part is 0
    #             list_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
    #             counter += 1
    #
    # if counter != 0:
    #     distance_to_list, created = Distance_to_List.objects.update_or_create(song_id_id=added_song.pk,
    #                                                                           list_id_id=the_list.pk,
    #                                                                           distance_Type=distance_type,
    #                                                              defaults={'distance': list_to_song_distance / counter})
    #
    # else:
    if distances is not None:
        distance_to_list, created = Distance_to_List.objects.update_or_create(song_id_id=added_song.pk,
                                                                              list_id_id=the_list.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': distances})

        distance_to_list.save()

    return

@shared_task()
def handle_added_song(song_id, user_id):
    # calculates the distances of this song to all other songs already in the database
    song = Song.objects.get(pk=song_id)


    save_all_representations(song_id)

    load_w2v_representations(1000, song_id)
    print('w2v loaded, distances saved')

    load_pca_mel_representations(1000, song_id)
    print('spec reprs loaded and distances saved')

    load_gru_mel_representations(500, song_id)
    print('gru mel distances saved')

    load_lstm_mfcc_representations(500, song_id)
    print('lstm mel distances saved')

    load_pca_tf_idf_representations(1000, song_id)
    print('tf_idf loaded, distances saved')

    # calculates the distance of this song to the user
    save_user_distances(song_id, user_id, "PCA_TF-idf")
    save_user_distances(song_id, user_id, "W2V")
    save_user_distances(song_id, user_id, "PCA_MEL")
    save_user_distances(song_id, user_id, "GRU_MEL")
    save_user_distances(song_id, user_id, "LSTM_MFCC")
    #  calculates the distance of this song to all of the lists the current
    # user created
    lists = List.objects.all().filter(user_id_id=user_id)
    for l in lists:
        save_list_distances(song_id, l.pk, user_id, "PCA_TF-idf")
        save_list_distances(song_id, l.pk, user_id, "W2V")
        save_list_distances(song_id, l.pk, user_id, "PCA_MEL")
        save_list_distances(song_id, l.pk, user_id, "GRU_MEL")
        save_list_distances(song_id, l.pk, user_id, "LSTM_MFCC")




@shared_task()
def load_lstm_mfcc_representations(chunk_size, s_id):
    count = Song.objects.all().exclude(audio=False).count()
    s = Song.objects.get(pk=s_id)
    representations = numpy.empty([count, 5168])
    i = 0
    j = 0
    for song in Song.objects.all().order_by('id').exclude(audio=False).only('id'):
        if (i % chunk_size == 0) and (i != 0):
            save_distances(s_id, s.lstm_mfcc_representation, representations, LSTM_MFCC_THRESHOLD, 'LSTM_MFCC', j * chunk_size,
                           (j + 1) * chunk_size)
            representations[i % chunk_size] = song.get_lstm_mfcc_representation()
            j = j + 1
        elif i >= (count - 1):
            representations = representations[:i % chunk_size]
            save_distances(s_id, s.lstm_mfcc_representation, representations, LSTM_MFCC_THRESHOLD, 'LSTM_MFCC', j * chunk_size,
                           i)
            break
        else:
            representations[i % chunk_size] = song.get_lstm_mfcc_representation()
            print(i, 'lstm mfcc', str(i % chunk_size))

        i = i + 1


@shared_task()
def load_pca_mel_representations(chunk_size, s_id):
    count = Song.objects.all().exclude(audio=False).count()
    s = Song.objects.get(pk=s_id)
    representations = numpy.empty([count, 320])
    i = 0
    j = 0
    for song in Song.objects.all().order_by('id').exclude(audio=False).only('pca_mel_representation'):
        if (i % chunk_size == 0) and (i != 0):
            save_distances(s_id, s.pca_mel_representation, representations, PCA_MEL_THRESHOLD, 'PCA_MEL', j * chunk_size,
                           (j + 1) * chunk_size)
            representations[i % chunk_size] = song.get_pca_mel_representation()
            j = j + 1
        elif i >= (count -1):
            representations = representations[:i % chunk_size]
            save_distances(s_id, s.pca_mel_representation, representations, PCA_MEL_THRESHOLD, 'PCA_MEL', j * chunk_size, i)
            break
        else:
            representations[i % chunk_size] = song.get_pca_mel_representation()
            print(i, 'pca mel', str(i % chunk_size))

        i = i + 1

@shared_task()
def load_gru_mel_representations(chunk_size, s_id):
    count = Song.objects.all().exclude(audio=False).count()
    s = Song.objects.get(pk=s_id)
    representations = numpy.empty([count, 5712])
    i = 0
    j = 0
    for song in Song.objects.all().order_by('id').exclude(audio=False).only('id'):
        if (i % chunk_size == 0) and (i != 0):
            save_distances(s_id, s.gru_mel_representation, representations, GRU_MEL_THRESHOLD, 'GRU_MEL', j * chunk_size,
                           (j + 1) * chunk_size)
            representations[i % chunk_size] = song.get_gru_mel_representation()
            j = j + 1
        elif i >= (count -1):
            representations = representations[:i % chunk_size]
            save_distances(s_id, s.gru_mel_representation, representations, GRU_MEL_THRESHOLD, 'GRU_MEL', j * chunk_size, i)
            break
        else:
            representations[i % chunk_size] = song.get_gru_mel_representation()
            print(i, 'gru_mel')

        i = i + 1



@shared_task()
def load_pca_tf_idf_representations(chunk_size, s_id):
    count = Song.objects.all().exclude(audio=False).count()
    s = Song.objects.get(pk=s_id)
    representations = numpy.empty([count, 4457])
    i = 0
    j = 0
    for song in Song.objects.all().order_by('id').exclude(audio=False).only('id'):
        if (i % chunk_size == 0) and (i != 0):
            save_distances(s_id, s.pca_tf_idf_representation, representations, PCA_TF_IDF_THRESHOLD, 'PCA_TF-idf', j * chunk_size,
                           (j + 1) * chunk_size)
            representations[i % chunk_size] = song.get_pca_tf_idf_representation()
            j = j + 1
            print('distances', j, 'saved')
        elif i >= (count -1):
            representations = representations[:i% chunk_size]
            save_distances(s_id, s.pca_tf_idf_representation, representations, PCA_TF_IDF_THRESHOLD, 'PCA_TF-idf', j * chunk_size, i)
            break
        else:
            representations[i % chunk_size] = song.get_pca_tf_idf_representation()
            print(i, 'pca_tf_idf')

        i = i + 1



@shared_task()
def load_w2v_representations(chunk_size, s_id):
    print('starting with w2v represenations')
    count = Song.objects.all().count()
    print(count)
    s = Song.objects.get(pk=s_id)
    representations = numpy.empty([chunk_size, 300])
    i = 0
    j = 0
    for song in Song.objects.all().order_by('id').exclude(audio=False).only('w2v_representation'):
        if (i % chunk_size == 0) and (i != 0):
            save_distances(s_id, s.w2v_representation, representations, W2V_THRESHOLD, 'W2V', j * chunk_size,
                           (j + 1) * chunk_size)
            representations[i % chunk_size] = song.get_W2V_representation()
            j = j + 1
        elif i >= (count -1) :
            representations = representations[:i% chunk_size]
            save_distances(s_id, s.w2v_representation, representations, W2V_THRESHOLD, 'W2V', j * chunk_size, i)
            break
        else:
            representations[i % chunk_size] = song.get_W2V_representation()
            print(i, 'w2v')

        i = i + 1

@shared_task()
def save_distances(song_id, song_representation, representations, threshold, distance_type, start_index, end_index):
    song = Song.objects.get(pk=song_id)
    print('distances', distance_type, 'to be calculated')
    try:
        distances = sklearn.metrics.pairwise.cosine_similarity(numpy.array(song_representation, dtype=float).reshape(1,-1), representations)
        distances = distances.reshape([(end_index-start_index)])
        print('distances calculated')
        i = 0
        print(start_index, end_index)
        for song_2 in Song.objects.all().order_by('id').exclude(audio=False).values_list('id', flat=True)[(start_index):(end_index-1)]:
            if song_id != song_2:
                if distances[i] > threshold:
                    print('got over the f***** if')
                    s = Song.objects.get(pk=song_2)
                    dist_1 = Distance(song_1=song, song_2=s, distance_Type=str(distance_type),
                                      distance=distances[i].item())
                    dist_2 = Distance(song_1=s, song_2=song, distance_Type=str(distance_type),
                                      distance=distances[i].item())
                    dist_1.save()
                    dist_2.save()
                    print('distance between' + str(song) + 'and' + str(s) + str(distances[i]) + 'saved')
                else:
                    print(str(i) + 'too small')

            i = i+1
    except Exception as e:
        print(e)

    print('distances', distance_type, 'saved')