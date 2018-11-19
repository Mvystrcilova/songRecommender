import pandas
import string
import urllib.request
from bs4 import BeautifulSoup

df = pandas.read_csv('~/Documents/matfyz/rocnikac/songs_with_lyrics', sep=';', quotechar='"', names=[ 'artist', 'songTitle', 'lyrics'], engine='python', error_bad_lines=False, usecols=[2,3,4])
df = df.drop_duplicates(subset=['artist', 'songTitle'])


for i, row in df.iterrows():

    try:
        textToSearch = row['artist'] + ' ' + row['songTitle']
        query = urllib.parse.quote(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        #     print('https://www.youtube.com' + vid['href'])

        vid = soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]
        l = 'https://www.youtube.com' + vid['href']
        df.at[i, 'link'] = l

        print(l)

    except:
        l = "no link for this video :("
        df.at[i, 'link'] = l
        print(row['artist'] + ' ' + row['songTitle'])
