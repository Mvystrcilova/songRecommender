import pandas
import re

txt = open('/Users/m_vys/Documents/matfyz/rocnikac/djangoApp/rocnikac/songRecommender/Logic/songs_for_database_2').read()
h = open('fixed_songs_for_database', 'a', encoding='utf-8')
g = open('csv_songs_for_database', 'a', encoding='utf=8')
array = txt.split(";")
song = []
for i in range(0,len(array)):
    if (i % 5 == 2):
        array[i] = array[i].replace('\n', '\t')
    song.append(array[i])
    if (i % 5 == 4):
        h.write(';'.join(song) + '\t')
        song = []

h.close()

df = pandas.read_csv('fixed_songs_for_database', sep=';', names=['title', 'artist', 'text', 'link', 'file_address'])
df.to_csv('csv_songs_for_database')
print(df.shape)
