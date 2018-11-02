from songRecommender.models import Song, Distance
import pandas
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer



def get_TFidf_distance(addedSong):
    # gets all songs from the database except the one we are dealing with
    # all_songs = Song.objects.all().order_by('-id')
    # saves them into a dataframe
    df = pandas.DataFrame(list(Song.objects.all().exclude(id=addedSong.pk).order_by('-id').values('text')))

    # adds the new songs lyrics to the rest of the lyrics
    songs = df['text'].tolist()

    # transforms the dataset into a matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix_train = tfidf_vectorizer.fit_transform(songs)  # finds the tfidf score with normalization

    return cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)[0]


# gets all the distances as attributes, all songs
# then adds two of the same distances to the Distances table in the database


def save_TFidf_distances(distances, addedSong):
    all_songs = Song.objects.all().order_by('-id')
    counter = 0
    for song in all_songs:
        if song.pk != addedSong.pk:
            dist_1 = Distance(song_1=song, song_2=addedSong, distance=distances[counter], distance_Type="TF-idf")
            dist_2 = Distance(song_1=addedSong, song_2=song, distance=distances[counter], distance_Type="TF-idf")
            dist_1.save()
            dist_2.save()
            counter += 1
    return
