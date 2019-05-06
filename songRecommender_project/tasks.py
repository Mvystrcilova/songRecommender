from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task

from songRecommender.models import Song, List, Distance, Distance_to_List, Distance_to_User, Song_in_List,\
    Profile
import sklearn, numpy
from django.db.models import Avg
from songRecommender.Logic.adding_songs import save_all_representations

from songRecommender_project.settings import PCA_TF_IDF_THRESHOLD, W2V_THRESHOLD, LSTM_MFCC_THRESHOLD, PCA_MEL_THRESHOLD, GRU_MEL_THRESHOLD

app = Celery('tasks', broker='amqp://localhost')


@shared_task
def add(x, y):
    print(x+y)
    return x + y

def calculate_distance_of_added_song_to_lists(song_id, user_id, distance_Type):
    """
    calculates the similarity (which kind is specified by the distance_Type) of a newly added song specified by
    song_id to the lists of the user specified by user_id and save the new Distance_to_List instances into the database.
    :param song_id: the id of the song of which the similarity to the users lists is calculated
    :param user_id: the user whose lists similarity to the song is calculated
    :param distance_Type: the distance Type of which the calculated similarities are
    :return: None, just saves the Distance_to_List objects to the database
    """
    relevant_songs = Distance.objects.filter(song_1_id=song_id, song_2__song_in_list__list_id__user_id=user_id, distance_Type=distance_Type).values('id')
    relevant_lists = List.objects.filter(user_id_id=user_id, song_in_list__song_id_id__in=relevant_songs)

    for list in relevant_lists:
        songs_in_list = Song_in_List.objects.filter(list_id=list, song_id_id__in=relevant_songs)
        distance = Distance.objects.filter(song_2__song_in_list__in=songs_in_list, song_1_id=song_id, distance_Type=distance_Type).aggregate(total=Avg('distance'))['total']
        list_distance = Distance_to_List.objects.create(song_id_id=song_id, list_id=list, distance_Type=distance_Type, distance=distance)
        list_distance.save()


@shared_task
def recalculate_distances_for_relevant_lists(song_id, user_id):
    """
    recalculates the distances of the song specified by song_id to the lists
    of the user specified by user_id
    :param song_id: the song's id to which the similarity is recalculated
    :param user_id: the user's id whose lists is the similarity recalculated to
    :return: None
    """
    relevant_lists = List.objects.filter(user_id_id=user_id).only('id')
    for list in relevant_lists:
        recalculate_all_distances_to_list(song_id=song_id, list_id=list)

@shared_task
def recalculate_distances_to_user(song_id, cur_user_id, distance_type):
    """for every song in the database it recalculates
    the distance to every user and the distance to every list
    the current user has created"""

    relevant_song_ids = Distance.objects.filter(song_1_id=song_id, distance_Type=distance_type).values('song_2_id', 'distance')

    for s in relevant_song_ids:
        user_distance, created = Distance_to_User.objects.get_or_create(user_id_id=cur_user_id, song_id_id=s['song_2_id'], distance_Type=distance_type)
        if created:
            user_distance.distance = s['distance']
        else:
            user_distance.distance = user_distance.distance + s['distance']
        user_distance.save()


def recalculate_distances_to_list(song_id, list_id, distance_type):
    """
    recalculates the similarity (what kind is specified with distance_type) of the song
     specified by song_id to the list specified by list_id
    :param song_id: the song's id to which the similarity is recalculated
    :param list_id: the list's id to which the similarity is recalculated
    :param distance_type: specifies the type of similarity that is being recalculated
    :return: None
    """
    relevant_song_ids = Distance.objects.filter(song_1_id=song_id, distance_Type=distance_type).values('song_2_id', 'distance')

    for s in relevant_song_ids:
        list_distance, created = Distance_to_List.objects.get_or_create(list_id_id=list_id, song_id_id=s['song_2_id'],
                                                                        distance_Type=distance_type)
        if created:
            list_distance.distance = s['distance']
        else:
            list_distance.distance = (list_distance.distance + s['distance'])
        list_distance.save()

@shared_task
def calculate_all_distance_of_added_song_to_lists(song_id, user_id):
    """
    recalculates all implemented similarities of the added song specified by song_id to
    the lists which belong to the user specified by user_id
    :param song_id: the song's id which was added by the user
    :param user_id: the id of the user to whose lists the song similarity is calculated
    :return: None
    """
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'PCA_TF-idf')
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'W2V')
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'PCA_MEL')
    calculate_distance_of_added_song_to_lists(song_id,user_id, 'GRU_MEL')
    calculate_distance_of_added_song_to_lists(song_id, user_id, 'LSTM_MFCC')

@shared_task
def recalculate_all_distances_to_user(song_id, cur_user_id):
    """
    recalculates all implemented similarities of the added song specified by song_id
    to the user specified by user_id
    :param song_id: the song's id which was added by the user
    :param user_id: the id of the user to whom the song similarity is calculated
    :return: None
    """
    recalculate_distances_to_user(song_id, cur_user_id, 'PCA_Tf-idf')
    recalculate_distances_to_user(song_id, cur_user_id, 'W2V')
    recalculate_distances_to_user(song_id, cur_user_id, 'PCA_MEL')
    recalculate_distances_to_user(song_id, cur_user_id, 'GRU_MEL')
    recalculate_distances_to_user(song_id, cur_user_id, 'LSTM_MFCC')

@shared_task
def recalculate_all_distances_to_list(song_id, list_id):
    """
    recalculates all implemented similarities of the added song specified by song_id to
    the list which is specified by list_id
    :param song_id: the song's id which was added by the user
    :param list_id: the id of the list to which the song similarity is recalculated
    :return: None
    """
    recalculate_distances_to_list(song_id, list_id, 'PCA_Tf-idf')
    recalculate_distances_to_list(song_id, list_id, 'W2V')
    recalculate_distances_to_list(song_id, list_id, 'PCA_MEL')
    recalculate_distances_to_list(song_id, list_id, 'GRU_MEL')
    recalculate_distances_to_list(song_id, list_id, 'LSTM_MFCC')


@shared_task()
def handle_added_song(song_id):
    """
    saves the representations of the added song using the implemented methods and calculates
    all the distances of the new song to the songs that are already in the database
    :param song_id: the id of the added song
    :return: None
    """

    save_all_representations(song_id)

    load_w2v_representations(10000, song_id)
    print('w2v loaded, distances saved')

    if Song.objects.get(id=song_id).audio:
        load_pca_mel_representations(10000, song_id)
        print('spec reprs loaded and distances saved')

        load_gru_mel_representations(5000, song_id)
        print('gru mel distances saved')

        load_lstm_mfcc_representations(5000, song_id)
        print('lstm mel distances saved')

    load_pca_tf_idf_representations(7000, song_id)
    print('tf_idf loaded, distances saved')





@shared_task
def recalculate_distanced_when_new_song_added(song_id):
    """
    calculates the distances of the newly added song to all the users that are in the database
    :param song_id: the id of the newly added song
    :return: None
    """
    for user_id in Profile.objects.all().values_list('user_id', flat=True):
        recalculate_all_distances_to_user.delay(song_id, user_id)
        calculate_all_distance_of_added_song_to_lists.delay(song_id, user_id)

@shared_task()
def load_lstm_mfcc_representations(chunk_size, s_id):
    """
    loads the lstm_mfcc representations of all songs that are in the database by chunks into a numpy array and then calls
    a function to calculate the similarity of the song's specified by s_id lstm_mfcc representation to the chunk of songs
    from the database that is currently being processed
    :param chunk_size: the number of instances of Song whose lstm_mfcc representations are loaded into a numpy array
    :param s_id: the id of the songs to which all the similarities are calculated to
    :return: None
    """
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
    """
    loads the pca_mel representations of all songs that are in the database by chunks into a numpy array and then calls
    a function to calculate the similarity of the song's specified by s_id pca_mel representation to the chunk of songs
    from the database that is currently being processed
    :param chunk_size: the number of instances of Song whose pca_mel representations are loaded into a numpy array
    :param s_id: the id of the songs to which all the similarities are calculated to
    :return: None
    """
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
    """
    loads the gru_mel representations of all songs that are in the database by chunks into a numpy array and then calls
    a function to calculate the similarity of the song's specified by s_id gru_mel representation to the chunk of songs
    from the database that is currently being processed
    :param chunk_size: the number of instances of Song whose gru_mel representations are loaded into a numpy array
    :param s_id: the id of the songs to which all the similarities are calculated to
    :return: None
    """
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
    """
        loads the pca_tf_idf representations of all songs that are in the database by chunks into a numpy array and then calls
        a function to calculate the similarity of the song's specified by s_id pca_tf_idf representation to the chunk of songs
        from the database that is currently being processed
        :param chunk_size: the number of instances of Song whose pca_tf_idf representations are loaded into a numpy array
        :param s_id: the id of the songs to which all the similarities are calculated to
        :return: None
        """
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
    """
    loads the w2v representations of all songs that are in the database by chunks into a numpy array and then calls
    a function to calculate the similarity of the song's specified by s_id w2v representation to the chunk of songs
    from the database that is currently being processed
    :param chunk_size: the number of instances of Song whose w2v representations are loaded into a numpy array
    :param s_id: the id of the songs to which all the similarities are calculated to
    :return: None
    """
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
    """
    calculates and saves the similarities of songs specified by song_id to each of the songs whose representations are in the
    representations parameter. These songs are songs from the web application whose audio property is set to True. The songs are given to this
    method in chunks and the start_index and end_index help specify which song the representations in the representations matrix
    belong to as it is necessary to acquire their ids to save the distance between the song specified by song_id and them.
    It all the similarities of this song to the others are saved if it is not the similarity of the
    song to itself and if the similarity is bigger then the threshold specified in settings.py
    :param song_id: (int) the id of the song toward which all the similarities will be calculated
    :param song_representation: (numpy array) a numpy array with the representation of the song specified by song_id. The representation
    type corresponds to the distance_type.
    :param representations: (numpu array) the representations of all the other songs whose similarity to the song specified
    by song_id is beign calculated
    :param threshold: (float32) the threshold for the particular distance type
    :param distance_type: (string) a string specifying the distance type of the method whose similarities are computed
    :param start_index: (int) the start index of the list of songs in the database which is the first in the representation numpy matrix
    :param end_index: (int) the last index of the slits of songs in the database which is the last in the representation numpy matrix
    :return: None
    """
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
