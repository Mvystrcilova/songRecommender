from songRecommender.data.select_song_subset import get_songs_that_have_distances
import os
import pandas
from songRecommender.models import Distance, Song


def load_distances():
    directory_in_string = "/Users/m_vys/Documents/matfyz/rocnikac/distances_subset/"
    # songs_with_distances = get_songs_that_have_distances("/Users/m_vys/Documents/matfyz/rocnikac/distances_subset/")
    directory = os.fsencode(directory_in_string)
    for f in os.listdir(directory):
        filename = os.fsdecode(f)
        artist = filename.split('_')[1]
        song_name = filename.split('_')[2]

        df = pandas.read_csv("/Users/m_vys/Documents/matfyz/rocnikac/distances_subset/" + filename, sep=';', names=['songTitle','artist', 'distance',], engine='python', error_bad_lines=False, usecols=[0, 1, 2])
        for i,row in df.iterrows():
            try:
                song_1 = Song.objects.get(song_name=song_name, artist=artist)
                song_2 = Song.objects.get(song_name=df.at[i, 'songTitle'], artist=df.at[i, 'artist'])
                distance, created = Distance.objects.get_or_create(song_1=song_1, song_2=song_2, distance=df.at[i,'distance'], distance_Type="TF-idf")
                if created:
                    distance_2 = Distance(song_1=song_2, song_2=song_1, distance=df.at[i,'distance'], distance_Type="TF-idf")
                    distance_2.save()

            except:
                pass
