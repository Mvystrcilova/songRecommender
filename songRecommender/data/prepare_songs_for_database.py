import pandas
import string
import urllib.request
from bs4 import BeautifulSoup
import time
import re

"""the change_youtube_url method is here because otherwise
it would have to import something from django and configure
settings for this directory although it doesnt have much to
with the songRecommender app"""

# sed '/https:\/\/www.youtube.com\/embed\/*/ s/$/;/' songs_with_l_and_l > output_songs

def change_youtube_url(url):
    """Takes the youtube url from either the address bar
     or the one from the share option under the Youtube video
     and changes it to an embedable one.

     Parameters
     ---------
     url : str
        the youtube url from the song website
    """

    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return "https://www.youtube.com/embed/" + youtube_regex_match.group(6)

    return youtube_regex_match


df = pandas.read_csv('~/Documents/matfyz/rocnikac/songs_with_lyrics', sep=';', quotechar='"',
                     names=['artist', 'songTitle', 'lyrics'], engine='python',
                     error_bad_lines=False, usecols=[2, 3, 4])
df = df.drop_duplicates(subset=['artist', 'songTitle'])

h = open('songs_for_database', 'a', encoding='utf8')

for i, row in df.iterrows():

    if i >= 19737:
        try:
            textToSearch = row['artist'] + ' ' + row['songTitle']
            query = urllib.parse.quote(textToSearch)
            url = "https://www.youtube.com/results?search_query=" + query
            response = urllib.request.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            # for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            #     print('https://www.youtube.com' + vid['href'])
            if ((i % 500) == 0) and (i != 0):
                time.sleep(600)
            vid = soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]
            l = 'https://www.youtube.com' + vid['href']
            df.at[i, 'link'] = change_youtube_url(l)
            h.write(df.at[i, 'songTitle'] + '\t' + df.at[i, 'artist'] + '\t' + df.at[i, 'lyrics'] +
                    '\t' + df.at[i, 'link'] + '\n')
            print(l)

        except:
            h.close()
            print(i)
            print(row['artist'] + ' ' + row['songTitle'])
            break
