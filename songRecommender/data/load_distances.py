# from songRecommender.data.select_song_subset import get_songs_that_have_distances
import os
import pandas
from songRecommender.models import Distance, Song
import numpy

def load_distances(distance_matrix, distance_type, threshold):
    distances = numpy.load(distance_matrix)
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
                        if distances[i][j] > threshold:
                            distance, created = Distance.objects.get_or_create(song_1=song_1, song_2=song_2,
                                                                               distance=distances[i][j],
                                                                               distance_Type=distance_type)
                            if created:
                                distance_2 = Distance(song_1=song_2, song_2=song_1, distance=distances[i][j],
                                                      distance_Type=distance_type)
                                distance_2.save()
                        else:
                            pass
                    except:
                        print(row['songTitle'], row['artist'], 'and', row_2['songTitle'], row_2['artist'])


