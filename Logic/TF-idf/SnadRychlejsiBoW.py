import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas
import numpy as np

df = pandas.read_csv('songs_with_lyrics', sep=';', quotechar='"', names=['userID', 'songID', 'artist', 'songTitle', 'lyrics'], engine='python', error_bad_lines=False)

simpleDF = df.drop_duplicates(subset=['artist', 'songTitle'], keep='first')

result = []
users = {}

for i in range(0, df.shape[0]):
    if df.iat[i, 0] in users.keys():
        users[df.iat[i, 0]].append((df.iat[i, 2], df.iat[i, 3]))
    else:
        users[df.iat[i, 0]] = [(df.iat[i, 2], df.iat[i, 3])]

songs = simpleDF['lyrics'].tolist()

valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

vectorizer = CountVectorizer(input=songs, stop_words=None)
matrix = vectorizer.fit_transform(songs)
print(vectorizer)

counter = 0
for row in simpleDF.itertuples():
    filename = 'song' + '_' + getattr(row, "artist") + '_' + getattr(row, "songTitle")
    fName = ''.join(c for c in filename if c in valid_chars)
    ar = cosine_similarity(matrix[counter], matrix)
    counter += 1
    with open(fName, 'w') as songFile:
        songFile.write(getattr(row, "artist") + ' ' + getattr(row, "songTitle") + '\n')
        finalList = []

        index = 0
        for row2 in simpleDF.itertuples():
            count = 0
            tup = (getattr(row2, "artist"), getattr(row2, "songTitle"), repr(ar[0][index]))
            index += 1
            finalList.append(tup)

            # spocita se median vzdalenosti
            median = np.median(ar[0])
            # spocita se prumerna vzdalenost
            average = sum(ar[0]) / len(ar[0])

        sortedList = sorted(finalList, key=lambda x: float(x[2]))
        for sL in sortedList:
            songFile.write('\t'.join(sL) + '\n')

        nums = "median= ", repr(median), "average= ", repr(average)
        songFile.write('\t'.join(nums) + '\n')
