import os
import pandas
import string

"""module selecting only a subset from all the data collected because it took too long to load
and I did not make it at home, will not be necessary later"""

def get_songs_that_have_distances(directory_in_string):
    """returns: names and artists of songs that we have the distance data available for"""
    dirctr = os.fsencode(directory_in_string)

    songs_with_distances = []
    for file in os.listdir(dirctr):
        filename = os.fsdecode(file)
        songs_with_distances.append((filename.split('_')[1], filename.split('_')[2]))

    return songs_with_distances


def reduce_file_with_distances(filename, songs_with_distances):
    """takes every file with all 16000 distances and only leaves 1761 left, for which we have all distances"""

    df = pandas.read_csv(filename, sep='\t', names=['artist', 'songTitle', 'distance', 'in_list'], engine='python', error_bad_lines=False, usecols=[0, 1, 2])
    new_filename = filename.split('/')[7] + '_subset'
    h = open(new_filename, 'a', encoding='utf-8')
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    for i, row in df.iterrows():
        if i > 0:
            song = (df.at[i, 'artist'], df.at[i, 'songTitle'])
            # new_song = ''.join(c for c in song if c in valid_chars)

            if song in songs_with_distances:
                line_to_write = df.at[i, 'songTitle'] + ';' + df.at[i, 'artist'] + ';' + df.at[i, 'distance'] + '\n'
                h.write(line_to_write)

    h.close()
    return


# directory_in_string = '/Users/m_vys/Documents/matfyz/rocnikac/soubory_s_userem'
# distances = get_songs_that_have_distances(directory_in_string)
#
# directory = os.fsencode(directory_in_string)
# for f in os.listdir(directory):
#     fname = "/Users/m_vys/Documents/matfyz/rocnikac/soubory_s_userem/" + os.fsdecode(f)
#     reduce_file_with_distances(fname, distances)