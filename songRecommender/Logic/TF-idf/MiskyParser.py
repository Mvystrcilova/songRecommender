from csv import reader
import re
f = open('jams.tsv', 'r', encoding='utf-8')
g = open('songdata.csv', 'r', encoding='utf-8')
h = open('songs_with_lyrics', 'a', encoding='utf-8')

lines1 = f.readlines()
result = []
line = 0
for x in lines1:
    if len(x.split('\t')) >= 4:
        tup = result.append(x.split('\t'))
        result.append(tup)
        line += 1

f.close()

lines2 = g.read()
tempRes = []
res = []
twoQuotes = True
oneWord = ""
wordCount = 0
for letter in lines2:
    if letter == '"':
        if twoQuotes:
            twoQuotes = False
        else:
            twoQuotes = True
    elif (letter == ',' or letter == '\n') and twoQuotes:
        tempRes.append(oneWord)
        oneWord = ""
        wordCount += 1
        if wordCount % 4 == 0:
            t = (tempRes[0], tempRes[1] , '"' + tempRes[3] + '"')
            res.append('\t'.join(t))
            tempRes.clear()
    else:
        oneWord += letter




g.close()

count = 0
for x in res:
    for y in result:
        if y is not None:
            if (y[3].lower() == x.split('\t')[1].lower()) and (y[2].lower() == x.split('\t')[0].lower()):
                t = (y[1] + '\t' + y[0], x)
                h.write('\t'.join(t) + '\n')

h.close()

