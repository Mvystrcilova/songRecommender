import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from songRecommender.models import Song, Distance


# from gensim.models.keyedvectors import KeyedVectors
# from songRecommender.Logic.DocSim import DocSim


# model_path = 'songRecommender/Logic/GoogleNews-vectors-negative300.bin'
# w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=True)


def get_TFidf_distance(addedSong):
    # gets all songs from the database except the one we are dealing with
    # saves them into a dataframe
    df = pandas.DataFrame(list(Song.objects.all().order_by('-id').values('text')))

    # adds the new songs lyrics to the rest of the lyrics
    songs = df['text'].tolist()

    # transforms the dataset into a matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix_train = tfidf_vectorizer.fit_transform(songs)  # finds the tfidf score with normalization

    return cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)[0]


# gets all the distances as attributes, all songs
# then adds two of the same distances to the Distances table in the database


def save_distances(distances, addedSong, dist_Type):
    all_songs = Song.objects.all().order_by('-id')
    counter = 0
    for song in all_songs:
        if song.pk != addedSong.pk:
            dist_1 = Distance(song_1=song, song_2=addedSong, distance=distances[counter], distance_Type=dist_Type)
            dist_2 = Distance(song_1=addedSong, song_2=song, distance=distances[counter], distance_Type=dist_Type)
            dist_1.save()
            dist_2.save()
            counter += 1
    return

# def get_W2V_distance(addedSong):
#     ds = DocSim(w2v_model)
#     df = pandas.DataFrame(list(Song.objects.all().order_by('-id').values('text')))
#
#     # adds the new songs lyrics to the rest of the lyrics
#     songs = df['text'].tolist()
#
#     return ds.calculate_similarity(addedSong.text, songs)
