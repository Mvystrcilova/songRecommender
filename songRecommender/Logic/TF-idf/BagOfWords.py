import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas
import numpy as np

f = open('songs_with_lyrics', 'r', encoding='utf-8')

#precte cely soubor s pisnickama (jedna tam muze byt vickrat)
lines2 = f.read()

songs = []
tempSongs = []
wordCount = 0
songsIncluded = []
result = []
oneWord = ""
twoQuotes = True
users =[[]]
userCount = 0

#parsuje text tak, ze oddeluje na tabulatory, akorat ze mezi lyricsama pisnicky a dalsi pisnickou neni tabulator
#pozna se to tak, ze lyricsy jsou ve dvojuvozovkach
for letter in lines2:
    #kdyz najde uvozovky, zmeni se podle toho jestli byl uvnitr jich nebo venku na to opacny
    if letter == '"':
        if twoQuotes:
            twoQuotes = False
        else:
            twoQuotes = True
    #kdyz najde tabulator nebo enter a neni mezi uvozovkama prida slovo do petice
    elif (letter == '\t' or letter == '\n') and twoQuotes:
        tempSongs.append(oneWord)
        oneWord = ""
        wordCount += 1

        #kdyz najde petici, znamena to, ze ma id usera, id skladby, nazev skladby, nazev skupiny a slova, vybere z toho (pokud to tam jeste neni) a prida ji do seznamu pisnicek
        if wordCount % 5 == 0:
            if (tempSongs[2], tempSongs[3]) not in songsIncluded:
                s = (tempSongs[2], tempSongs[3])
                songsIncluded.append(s)
                t = (tempSongs[0], tempSongs[1], tempSongs[2], tempSongs[3] + '"' + tempSongs[4] + '"')
                result.append(tempSongs[4])
                songs.append('\t'.join(t))
                inNoList = True
                thisList = []

            #jeste se kdyz najde petici podiva, jestli tohohle usera uz videla, kdyz ne, tak ho prida a prida k nemu najitou pisnicku, kdyz jo, tak k nemu jen prida najitou pisnicku
            for sublist in users:
                if not (tempSongs[0] in sublist):
                    continue
                else:
                    thisList = sublist
                    inNoList = False

            if inNoList:
                sList = [tempSongs[0]]
                users.append(sList)
                ns = (tempSongs[2], tempSongs[3])
                s = ('\t'.join(ns))
                users[users.index(sList)].append(s)
                userCount += 1
            elif not inNoList:
                ns = (tempSongs[2], tempSongs[3])
                s = ('\t'.join(ns))
                users[users.index(thisList)].append(s)
            tempSongs.clear()
    else:
        oneWord += letter

#udela ze vsech pisnicek vektor
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(result)
print(tfidf_matrix.shape)
shape = tfidf_matrix.shape

#aby se daly tvorit soubory s menama pisnicek
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

#pro kazdou pisnicku se vytrovri soubor, kam se zapise jmeno pisnicky, a postupne vzdalenost ke vsem ostatnim pisnickam s jejich jmeny
for s in songs:
    filename = 'song' + '_' + s.split('\t')[2] + '_' + s.split('\t')[3].split('"')[0]
    fName = ''.join(c for c in filename if c in valid_chars)
    h = open(fName, 'a', encoding='utf8')
    y = (s.split('\t')[2], s.split('\t')[3].split('"')[0])
    h.write('\t'.join(y) + '\n')
    i = songs.index(s)
    ar = cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix)
    finalList = []

    #tady se jeste zkontrolujou vsechny seznamy useru a kdyz jsou pisnicka pro kterou delame soubor a jina pisnicka u stejneho usera, zvysi se jim count o jeden
    #to se pak taky zapisuje do souboru
    for j in range(0, shape[0] - 1):
        sameList = 0
        for sublists in users:
            if '\t'.join(y) in sublists:
                firstZ = (songs[j].split('\t')[2], songs[j].split('\t')[3].split('"')[0])
                z = '\t'.join(firstZ)
                if z in sublists:
                    sameList = sameList + 1

        tup = (songs[j].split('\t')[2], songs[j].split('\t')[3].split('"')[0], repr(ar[0][j]), repr(sameList))
        finalList.append(tup)

    #spocita se median vzdalenosti
    median = np.median(ar[0])
    #spocita se prumerna vzdalenost
    average = sum(ar[0])/len(ar[0])

    #list kde je vsechno co se bude psat do souboru se setridi a pak po jednom zapisuje na radky
    sortedList = sorted(finalList, key=lambda x: float(x[2]))
    for sL in sortedList:
        h.write('\t'.join(sL) + '\n')

    nums = "median= ", repr(median), "average= ", repr(average)
    h.write("'\t".join(nums) + '\n')
    h.close()

