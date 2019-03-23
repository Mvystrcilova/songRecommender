# from songRecommender.data.select_song_subset import get_songs_that_have_distances
import os
import pandas
from songRecommender.models import Distance, Song
import  numpy

def load_distances():
    distances = numpy.load("/Users/m_vys/PycharmProjects/similarity_and_evaluation/distances/tf_idf_distances.npy")
    # songs_with_distances = get_songs_that_have_distances("/Users/m_vys/Documents/matfyz/rocnikac/distances_subset/")
    df = pandas.read_csv("/Users/m_vys/PycharmProjects/similarity_and_evaluation/useful_songs", sep=';',
                         names=['songTitle','artist'], index_col=False, header=None,
                         engine='python', error_bad_lines=False)
    for i, row in df.iterrows():
        if i < 1000:
            for j, row_2 in df.iterrows():
                if j < 1000:
                    try:
                        song_1 = Song.objects.get(song_name=row['songTitle'], artist=row['artist'])
                        song_2 = Song.objects.get(song_name=row_2['songTitle'], artist=row_2['artist'])
                        distance, created = Distance.objects.get_or_create(song_1=song_1, song_2=song_2,
                                                                           distance=distances[i][j], distance_Type="TF-idf")
                        if created:
                            distance_2 = Distance(song_1=song_2, song_2=song_1, distance=distances[i][j],
                                                  distance_Type="TF-idf")
                            distance_2.save()

                    except:
                        pass
