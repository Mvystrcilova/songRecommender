import string
import pandas
import numpy as np

df = pandas.read_csv('~/Documents/matfyz/rocnikac/songs_with_lyrics', sep=';', quotechar='"', names=['userID', 'songId', 'artist', 'songTitle', 'lyrics'], engine='python', error_bad_lines=False)

result = df.sort_values(by=['userID'])



