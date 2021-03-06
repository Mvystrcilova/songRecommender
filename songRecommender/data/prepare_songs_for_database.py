from __future__ import unicode_literals
import pandas
import string
import urllib.request
from bs4 import BeautifulSoup
import time
import re
import youtube_dl
from songRecommender_project.settings import MP3FILES_DIR
import os

"""the change_youtube_url method is here because otherwise
it would have to import something from django and configure
settings for this directory although it doesnt have much to
with the songRecommender app"""

# sed '/https:\/\/www.youtube.com\/embed\/*/ s/$/;/' songs_with_l_and_l > output_songs

def change_youtube_url(url):
    """
    Takes the youtube url from either the address bar
     or the one from the share option under the Youtube video
     and changes it to an embedable one.

     is not used in the application anywhere
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

######## From here on it is a script that was used to get the .mp3 files of the songs in the database

df = pandas.read_csv('~/Documents/matfyz/songRecommender_project/data/songs_with_lyrics', sep=';', quotechar='"',
                     names=['artist', 'songTitle', 'lyrics'], engine='python',
                     error_bad_lines=False, usecols=[2, 3, 4])
df = df.drop_duplicates(subset=['artist', 'songTitle'])

h = open('songs_for_database_2', 'a', encoding='utf8')

for i, row in df.iterrows():

    if i > 111370:
        try:
            textToSearch = row['artist'] + ' ' + row['songTitle']
            query = urllib.parse.quote(textToSearch)
            url = "https://www.youtube.com/results?search_query=" + query
            response = urllib.request.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            if ((i % 500) == 0) and (i != 0):
                time.sleep(600)
            vid = soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]

            df.at[i, 'link'] = change_youtube_url(vid)
            name = df.at[i,'songTitle'] + '-' + df.at[i, 'artist'] + ".mp3"
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': MP3FILES_DIR + "%(title)s.%(ext)s"
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vid])
                info_dict = ydl.extract_info(vid, download=False)
                df.at[i, 'link_on_disc'] = MP3FILES_DIR + info_dict.get('title', None) + ".mp3"
            h.write(df.at[i, 'songTitle'] + ';' + df.at[i, 'artist'] + ';' + "\"" + df.at[i, 'lyrics'] +"\""
                    ';' + df.at[i, 'link'] + ';' + df.at[i, 'link_on_disc'] + ";\n")
            print(vid)

        except youtube_dl.utils.DownloadError:
            h.close()
            print(i)
            print(row['artist'] + ' ' + row['songTitle'])
            break

