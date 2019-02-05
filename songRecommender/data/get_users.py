import string
import pandas
import numpy as np

df = pandas.read_csv('~/Documents/matfyz/rocnikac/songs_with_lyrics', sep=';', quotechar='"', names=['userID', 'songId', 'artist', 'songTitle', 'lyrics'], engine='python', error_bad_lines=False)

users = df.drop_duplicates(subset=['userID'])
print("The number of unique users is: " + str(users.shape[0]))
ds = df[['songTitle', 'userID']].groupby('userID').agg(['count'])
hist_ds = df.hist(column=['userID', 'songTitle'], by='userID')
dSong = df[['songTitle', 'userID']].groupby('songTitle').agg(['count'])
mean = ds.mean(axis=0)
meanSong = dSong.mean(axis=0)
users = users.sort_values(by=['userID'])

result = df.sort_values(by=['userID'])

print("hotovo")



