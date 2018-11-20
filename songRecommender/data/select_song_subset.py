import os
import pandas
import string

def get_songs_that_have_distances():
    directory_in_string = '/Users/m_vys/Documents/matfyz/rocnikac/soubory_s_userem'
    directory = os.fsencode(directory_in_string)

    songs_with_distances = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        songs_with_distances.append(filename.split('_')[1] + '\t' + filename.split('_')[2])

    return songs_with_distances

def reduce_file_with_distances(file, songs_with_distances):
    df = pandas.read_csv(file, sep='\t', names=['artist', 'songTitle', 'distance'], engine='python', error_bad_lines=False)
    filename = os.fsdecode(file)
    new_filename = filename + '_subset'
    h = open(new_filename, 'a', encoding='utf-8')
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    for i, row in df.iterrows():
        song = getattr(row, "songTitle") + '\t' + getattr(row, "artist")
        new_song = ''.join(c for c in song if c in valid_chars)

        if new_song in songs_with_distances:
            h.write()
    return
