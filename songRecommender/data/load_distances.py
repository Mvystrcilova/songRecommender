# from songRecommender.data.select_song_subset import get_songs_that_have_distances
import os
import pandas
from songRecommender.models import Distance, Song
import numpy
from rocnikac.settings import PCA_TF_IDF_THRESHOLD, W2V_THRESHOLD, LSTM_MFCC_THRESHOLD, GRU_MEL_THRESHOLD, PCA_MEL_THRESHOLD
def load_distances(distance_matrix, distance_type, threshold):
    distances = numpy.load(distance_matrix)
    distances[distances < threshold] = 0
    indexes = numpy.transpose(numpy.nonzero(distances))
    print(distance_type, 'has shape', indexes.shape)
    df = pandas.read_csv("rocnikac/useful_songs", sep=';',
                         names=['songTitle','artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)
    for i in indexes:
        if i[0] >= 15000:
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

def load_distances_faster():

    pass

def load_all_distances():
    # load_distances('rocnikac/distances/pca_tf_idf_distances.npy', 'PCA_TF_idf', PCA_TF_IDF_THRESHOLD)
    # load_distances('rocnikac/distances/w2v_distances.npy', 'W2V', W2V_THRESHOLD)
    load_distances('rocnikac/distances/pca_melspectrogram_distances.npy', 'PCA_MEL', PCA_MEL_THRESHOLD)
    load_distances('rocnikac/distances/lstm_mfcc_distances.npy', 'LSTM_MFCC', LSTM_MFCC_THRESHOLD)
    load_distances('rocnikac/distances/gru_mel_distances_5712.npy', 'GRU_MEL', GRU_MEL_THRESHOLD)


def load_all_representations():
    load_pca_tf_idf_representations_to_db('rocnikac/representations/pca_tf_idf_representations.npy')
    load_w2v_representations_to_db('rocnikac/representations/w2v_representations.npy')
    load_pca_mel_representations_to_db('rocnikac/representations/pca_mel_representations.npy')
    load_gru_mel_representations_to_db('rocnikac/representations/GRU_mel_representations_5712.npy')
    load_lstm_mfcc_representations_to_db('rocnikac/representations/lstm_mfcc_representations.npy')


def load_pca_tf_idf_representations_to_db(representation_matrix):
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("rocnikac/useful_songs", sep=';',
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
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("rocnikac/useful_songs", sep=';',
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
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("rocnikac/useful_songs", sep=';',
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
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("rocnikac/useful_songs", sep=';',
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
    representations = numpy.load(representation_matrix)
    df = pandas.read_csv("rocnikac/useful_songs", sep=';',
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
    df = pandas.read_csv("rocnikac/not_empty_songs_relative_path.txt", sep=';', header=None, index_col=False, names=['artist', 'title', 'lyrics', 'link', 'path'])
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