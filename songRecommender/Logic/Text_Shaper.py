import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from songRecommender.models import Song, Distance
import pandas

import gensim
from gensim.models.keyedvectors import KeyedVectors
from songRecommender.Logic.DocSim import DocSim


# model_path = 'songRecommender/Logic/GoogleNews-vectors-negative300.bin'
# w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=True, limit=200000)
# w2v_model.save('w2v_subset')

w2v_model = KeyedVectors.load('w2v_subset', mmap='r')

def get_TFidf_distance(addedSong):
    """gets all songs from the database except the one we are dealing with,
    computes the distances using TF-idf and saves them into a dataframe"""

    df = pandas.DataFrame(list(Song.objects.all().order_by('-id').values('text')))

    # adds the new songs lyrics to the rest of the lyrics
    songs = df['text'].tolist()

    # transforms the dataset into a matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix_train = tfidf_vectorizer.fit_transform(songs)  # finds the tfidf score with normalization

    return cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)[0]


def save_distances(distances, addedSong, dist_Type):
    """gets all the distances as attributes,
    finds all songs in database and stores new objects of the Distance
    into the Distance Table"""

    all_songs = Song.objects.all().order_by('-id')
    counter = 0
    # for every song it gets its data and added songs data and saves distance
    for song in all_songs:
        if song.pk != addedSong.pk: #checks if the processed and added song are not the same
            dist_1 = Distance(song_1=song, song_2=addedSong, distance=distances[counter], distance_Type=dist_Type)
            dist_2 = Distance(song_1=addedSong, song_2=song, distance=distances[counter], distance_Type=dist_Type)
            dist_1.save()
            dist_2.save()
            counter += 1
    return


def get_W2V_distance(addedSong):
    """gets all songs from the database except the one we are dealing with,
    computes the distances using W2V and saves them into a dataframe"""
    ds = DocSim(w2v_model)
    df = pandas.DataFrame(list(Song.objects.all().order_by('-id').values('text')))

    # adds the new songs lyrics to the rest of the lyrics
    songs = df['text'].tolist()

    return ds.calculate_similarity(addedSong.text, songs)
