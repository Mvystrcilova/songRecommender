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
from songRecommender_project.settings import W2V_model, TF_idf_model
from keras.models import model_from_json

from songRecommender_project.settings import PCA_TF_IDF_THRESHOLD, W2V_THRESHOLD, LSTM_MFCC_THRESHOLD, PCA_MEL_THRESHOLD, GRU_MEL_THRESHOLD

app = Celery('tasks', broker='amqp://localhost')


@shared_task
def add(x, y):
    print(x+y)
    return x + y

def calculate_distance_of_added_song_to_lists(song_id, user_id, distance_Type):
    relevant_songs = Distance.objects.filter(song_1_id=song_id, song_2__song_in_list__list_id__user_id=user_id, distance_Type=distance_Type).values('id')
    relevant_lists = List.objects.filter(user_id_id=user_id, song_in_list__song_id_id__in=relevant_songs)

    for list in relevant_lists:
        songs_in_list = Song_in_List.objects.filter(list_id=list, song_id_id__in=relevant_songs)
        distance = Distance.objects.filter(song_2__song_in_list__in=songs_in_list, song_1_id=song_id, distance_Type=distance_Type).aggregate(total=Avg('distance'))['total']
        list_distance = Distance_to_List.objects.create(song_id_id=song_id, list_id=list, distance_Type=distance_Type, distance=distance)
        list_distance.save()


@shared_task
def recalculate_distances_for_relevant_lists(song_id, user_id):
    relevant_lists = List.objects.filter(user_id_id=user_id).only('id')
    for list in relevant_lists:
        recalculate_all_distances_to_list(song_id=song_id, list_id=list)

@shared_task
def recalculate_distances_to_user(song_id, cur_user_id, distance_type):
    """for every song in the database it recalculates
    the distance to every user and the distance to every list
    the current user has created"""

    relevant_song_ids = Distance.objects.filter(song_1_id=song_id, distance_Type=distance_type).values('song_2_id', 'distance')

    num_of_played_songs = Played_Song.objects.filter(user_id_id=cur_user_id).count()
    for s in relevant_song_ids:
        user_distance, created = Distance_to_User.objects.get_or_create(user_id_id=cur_user_id, song_id_id=s['song_2_id'], distance_Type=distance_type)
        if created:
            user_distance.distance = s['distance']
        else:
            user_distance.distance = user_distance.distance + s['distance']
        user_distance.save()


def recalculate_distances_to_list(song_id, list_id, distance_type):
    relevant_song_ids = Distance.objects.filter(song_1_id=song_id, distance_Type=distance_type).values('song_2_id', 'distance')
    num_of_songs_in_list = Song_in_List.objects.filter(list_id_id = list_id).count()

    for s in relevant_song_ids:
        list_distance, created = Distance_to_List.objects.get_or_create(list_id_id=list_id, song_id_id=s['song_2_id'],
                                                                        distance_Type=distance_type)
        if created:
            list_distance.distance = s['distance']
        else:
            list_distance.distance = (list_distance.distance + s['distance'])
        list_distance.save()


def calculate_all_distance_of_added_song_to_lists(song_id, user_id):
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'PCA_TF-idf')
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'W2V')
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'PCA_MEL')
    calculate_distance_of_added_song_to_lists(song_id,user_id, 'GRU_MEL')
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'LSTM_MFCC')

@shared_task
def recalculate_all_distances_to_user(song_id, cur_user_id):
    recalculate_distances_to_user(song_id, cur_user_id, 'PCA_Tf-idf')
    recalculate_distances_to_user(song_id, cur_user_id, 'W2V')
    recalculate_distances_to_user(song_id, cur_user_id, 'PCA_MEL')
    recalculate_distances_to_user(song_id, cur_user_id, 'GRU_MEL')
    recalculate_distances_to_user(song_id, cur_user_id, 'LSTM_MFCC')

@shared_task
def recalculate_all_distances_to_list(song_id, list_id):
    recalculate_distances_to_list(song_id, list_id, 'PCA_Tf-idf')
    recalculate_distances_to_list(song_id, list_id, 'W2V')
    recalculate_distances_to_list(song_id, list_id, 'PCA_MEL')
    recalculate_distances_to_list(song_id, list_id, 'GRU_MEL')
    recalculate_distances_to_list(song_id, list_id, 'LSTM_MFCC')


@shared_task()
def handle_added_song(song_id, user_id):
    # calculates the distances of this song to all other songs already in the database

    save_all_representations(song_id)

    load_w2v_representations(5000, song_id)
    print('w2v loaded, distances saved')

    if Song.objects.get(id=song_id).audio:
        load_pca_mel_representations(5000, song_id)
        print('spec reprs loaded and distances saved')

        load_gru_mel_representations(3000, song_id)
        print('gru mel distances saved')

        load_lstm_mfcc_representations(3000, song_id)
        print('lstm mel distances saved')

    load_pca_tf_idf_representations(5000, song_id)
    print('tf_idf loaded, distances saved')

    # calculates the distance of this song to the user
    for user_id in Profile.objects.all().values_list('user_id', flat=True):
        recalculate_all_distances_to_user(song_id, user_id)

    #  calculates the distance of this song to all of the lists the current
    # user created
        calculate_all_distance_of_added_song_to_lists(song_id, user_id)
    # lists = List.objects.all().filter(user_id_id=user_id)
    # for l in lists:
    #     recalculate_all_distances_to_list(song_id, l.pk)




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
