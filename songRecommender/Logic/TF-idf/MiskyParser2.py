h = open('song_name_ID', 'a', encoding='utf-8')
TT = open('train_triplets.txt', 'r', encoding='utf-8')
UT  = open('unique_tracks.txt', 'r', encoding='utf-8')

d1=[]
lines = TT.readlines()
for i in lines:
    dt = tuple(i.split('\t'))
    d1.append(dt)

for i in UT.read().split('\n'):
    tmp = i.split('<SEP>')
    for j in d1:
        if tmp[1] in j:
            complete = (j[1], tmp[3].replace('\n', ""), tmp[2], j[0], j[2].replace('\n', ""))
            print(j[1], ' ', tmp[3], ' ', j[0], ' ', j[2])
            h.write('\t'.join(complete) + '\n')

h.close()
