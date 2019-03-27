import pandas
from songRecommender.models import Song


def load_songs():
    songs = pandas.read_csv('~/Documents/matfyz/rocnikac/data/songs_with_lyrics', sep=';',
                            names=['bla', 'bla', 'artist', 'title', 'lyrics'],
                            usecols=[2,3,4], index_col=False, header=None)

    songs = songs.drop_duplicates(subset=['artist', 'title'])

    i = 0
    for song in songs.itertuples():
        if i < 1000:
            Song.objects.create(song_name=song.title, artist=song.artist, text=song.lyrics, link="Missing link")
            i += 1

