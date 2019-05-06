# from songRecommender.data.select_song_subset import get_songs_that_have_distances
import os
import pandas
from songRecommender.models import Distance, Song
import numpy
from songRecommender_project.settings import PCA_TF_IDF_THRESHOLD, W2V_THRESHOLD, LSTM_MFCC_THRESHOLD, GRU_MEL_THRESHOLD, PCA_MEL_THRESHOLD
def load_distances(distance_matrix, distance_type, threshold):
    """
    an method used to load distances into the application. It is possible to only load distances for the 16594 songs in
    useful songs where the indexes of the songs have to correspond to the similarities in the distance matrix.
    For each similarity, two instances of Distance are created and saved to the database.

    :param distance_matrix: a matrix of shape 16594x16594 where on position i,j is the similarity between song on the
    ith line and jth line in the "useful songs" file
    :param distance_type: distance_Type is the type of measure this distance matrix was calculated based on, can be
    one of those in models.Distance.distance_Type
    :param threshold: threshold for minimum similarity, if lower, the Distance instance between two songs is not created
    :return: None

    """
    distances = numpy.load(distance_matrix)
    distances[distances < threshold] = 0
    indexes = numpy.transpose(numpy.nonzero(distances))
    print(distance_type, 'has shape', indexes.shape)
    df = pandas.read_csv("songRecommender_project/useful_songs", sep=';',
                         names=['songTitle','artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)
    for i in indexes:
        if i[0] >= 3218:
            if i[0] > i[1]:
                try:
                    song_1 = Song.objects.get(song_name=df.iloc[i[0]]['songTitle'], artist=df.iloc[i[0]]['artist'])
                    song_2 = Song.objects.get(song_name=df.iloc[i[1]]['songTitle'], artist=df.iloc[i[1]]['artist'])

                    distance, created = Distance.objects.get_or_create(song_1=song_1, song_2=song_2,
                                                                       distance=distances[i[0]][i[1]],
                                                                       distance_Type=distance_type)
                    if created:
                        distance_2 = Distance(song_1=song_2, song_2=song_1, distance=distances[i[0]][i[1]],
                                              distance_Type=distance_type)
                        distance_2.save()
                        print(i[0], i[1],  distances[i[0]][i[1]])

                except Exception as e:
                    print(e)
                    print(df.iloc[i[0]]['songTitle'], df.iloc[i[0]]['artist'], ' and ', df.iloc[i[1]]['songTitle'], df.iloc[i[1]]['artist'])

                # print(i[0], distance_type)
    print(distance_type, 'saved')


def load_all_distances():
    """
    A one time function that can be used to load all distances for the 16594 songs in useful_songs into the database
    before the use of the web application.
    Can be uncommented in views.py and then called when accessing a SongDetail view

    :return: None
    """
    load_distances('songRecommender_project/distances/pca_tf_idf_distances.npy', 'PCA_TF-idf', PCA_TF_IDF_THRESHOLD)
    load_distances('songRecommender_project/distances/w2v_distances.npy', 'W2V', W2V_THRESHOLD)
    load_distances('songRecommender_project/distances/pca_melspectrogram_distances.npy', 'PCA_MEL', PCA_MEL_THRESHOLD)
    load_distances('songRecommender_project/distances/lstm_mfcc_distances.npy', 'LSTM_MFCC', LSTM_MFCC_THRESHOLD)
    load_distances('songRecommender_project/distances/gru_mel_distances_5712.npy', 'GRU_MEL', GRU_MEL_THRESHOLD)


def load_all_representations():
    """
     A one time function that can be used to load all song representations for the 16594 songs in useful_songs
    into the database before the use of the web application.
    Can be uncommented in views.py and then called when accessing a SongDetail view
    :return: None
    """
    load_pca_tf_idf_representations_to_db('songRecommender_project/representations/pca_tf_idf_representations.npy')
    load_w2v_representations_to_db('songRecommender_project/representations/w2v_representations.npy')
    load_pca_mel_representations_to_db('songRecommender_project/representations/pca_mel_representations.npy')
    load_gru_mel_representations_to_db('songRecommender_project/representations/GRU_mel_representations_5712.npy')
    load_lstm_mfcc_representations_to_db('songRecommender_project/representations/lstm_mfcc_representations.npy')


def load_pca_tf_idf_representations_to_db(representation_matrix):
    """
    a function that loads the PCA_Tf-idf representation of each song from "useful_songs" into the database
    :param representation_matrix: a matrix of shape 16594x4457 where in row i is the pca_tf-idf representation of the
    song on the ith line from useful_songs
    :return: None
    """
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("songRecommender_project/useful_songs", sep=';',
                         names=['songTitle', 'artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)

    for i, row in df.iterrows():
        try:
            song = Song.objects.get(song_name=row['songTitle'], artist=row['artist'])
            song.pca_tf_idf_representation = representations[i].tolist()
            song.save()
            print(i)
        except Exception as e:
            print(str(e) + str(i) + 'pca_tf_idf')
            print(i, row['songTitle'], row['artist'])


def load_w2v_representations_to_db(representation_matrix):
    """
    a function that loads the W2V representation of each song from "useful_songs" into the database
    :param representation_matrix: a matrix of shape 16594x300 where in row i is the w2v representation of the
    song on the ith line from useful_songs
    :return: None
    """
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("songRecommender_project/useful_songs", sep=';',
                         names=['songTitle', 'artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)

    for i, row in df.iterrows():
        try:
            song = Song.objects.get(song_name=row['songTitle'], artist=row['artist'])
            song.w2v_representation = representations[i].tolist()
            song.save()
            print(i)
        except Exception as e:
            print(str(e) + str(i) + 'w2v')
            print(i, row['songTitle'], row['artist'])



def load_lstm_mfcc_representations_to_db(representation_matrix):
    """
    a function that loads the LSTM_MFCC representation of each song from "useful_songs" into the database
    :param representation_matrix: a matrix of shape 16594x5712 where in row i is the lstm_mfcc representation of the
    song on the ith line from useful_songs
    :return: None
    """
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("songRecommender_project/useful_songs", sep=';',
                         names=['songTitle', 'artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)

    for i, row in df.iterrows():
            try:
                song = Song.objects.get(song_name=row['songTitle'], artist=row['artist'])
                song.lstm_mfcc_representation = representations[i].tolist()
                song.save()
                print(i, 'lstm_saved')
            except Exception as e:
                print(str(e) + str(i) + 'lstm_mfcc')
                print(i, row['songTitle'], row['artist'])


def load_pca_mel_representations_to_db(representation_matrix):
    """
    a function that loads the PCA_MEL representation of each song from "useful_songs" into the database
    :param representation_matrix: a matrix of shape 16594x5715 where in row i is the PCA_mel representation of the
    song on the ith line from useful_songs
    :return: None
    """
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("songRecommender_project/useful_songs", sep=';',
                         names=['songTitle', 'artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)

    for i, row in df.iterrows():
        try:
            song = Song.objects.get(song_name=row['songTitle'], artist=row['artist'])
            song.pca_mel_representation = representations[i].tolist()
            song.save()
            print(i, 'pca_mel')
        except Exception as e:
            print(str(e) + str(i) + 'pca_mel')
            print(i, row['songTitle'], row['artist'])



def load_gru_mel_representations_to_db(representation_matrix):
    """
        a function that loads the GRU_MEL representation of each song from "useful_songs" into the database
        :param representation_matrix: a matrix of shape 16594x5712 where in row i is the gru_mel representation of the
        song on the ith line from useful_songs
        :return: None
        """
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("songRecommender_project/useful_songs", sep=';',
                         names=['songTitle', 'artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)

    for i, row in df.iterrows():
        try:
            song = Song.objects.get(song_name=row['songTitle'], artist=row['artist'])
            song.gru_mel_representation = representations[i].tolist()
            song.save()
            print(i, 'gru_mel')
        except Exception as e:
            print(str(e) + str(i) + 'gru_mel')
            print(i, row['songTitle'], row['artist'])



def load_songs_to_database():
    """
    a function that loads the songs from "useful_songs" into the database
    It has to be run before the song representations and distances are loaded into the database.
    Can be uncommented in views.py and then called when accessing a SongDetail view.
    :return: None
    """
    df = pandas.read_csv("songRecommender_project/not_empty_songs_relative_path.txt", sep=';', header=None, index_col=False, names=['artist', 'title', 'lyrics', 'link', 'path'])
    if df.shape[0] == 16594:
        for i, row in df.iterrows():
            # try:
            #     song = Song.objects.get(song_name=row['title'], artist=row['artist'])
            # except:
            song = Song(song_name=row['title'], artist=row['artist'], text=row['lyrics'], link=row['link'],
                        link_on_disc=row['path'])
            song.save()
            print('song', i, 'saved')
    else:
        print("WTF JUST HAPPENED???")