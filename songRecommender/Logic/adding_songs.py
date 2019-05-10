from songRecommender.models import Song, Distance
import numpy, youtube_dl, re, urllib.request, librosa, os, scipy.sparse, glob, sklearn.metrics
import urllib.parse
from bs4 import BeautifulSoup
from songRecommender_project.settings import MP3FILES_DIR
from pydub import AudioSegment
from songRecommender_project.settings import GRU_Mel_graph, LSTM_MFCC_graph
from keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler
from pydub.playback import play

from songRecommender_project.settings import PCA_Tf_idf_model, W2V_model, GRU_Mel_model, PCA_Mel_model, LSTM_MFCC_model, TF_idf_model

from songRecommender_project.settings import n_fft, hop_length, n_mfcc, n_mels

import re
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    """
    sorts values numericaly
    :param value:
    :return: sorted values
    """
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def save_all_representations(song_id):
    """
    When a new song is added, this function collects a representation of it for each of the implemented methods
    if the download of the audio fails, only lyrics based methods are represented
    :param song_id: the id of the newly added song
    :return: None
    """

    song = Song.objects.get(pk=song_id)
    download_song_from_youtube(song)

    if song.audio:
        try:
            y, sr = get_audio_data(song)
            print(y, sr)

            ######## Saving simple audio representations ###############

            mel_spectrogram = retrieve_mel_spectrogram_representation(y, sr).reshape([1, 130560])
            mel_spectrogram = numpy.interp(mel_spectrogram, (mel_spectrogram.min(), mel_spectrogram.max()), (0, 1))
            print('the melspectrogram:')
            print(mel_spectrogram)

            mel_spectrogram = mel_spectrogram.reshape([1, 408, 320])
            print(mel_spectrogram.shape)
            mfcc = retrieve_mfcc_representation(y, sr).reshape([1, 82688])
            mfcc = numpy.interp(mfcc, (mfcc.min(), mfcc.max()), (0, 1))
            print('the mfcc:')
            print(mfcc)
            mfcc = mfcc.reshape([1, 646, 128])



            print('got mfcc repr')

            ############################# Saving more advanced audio representations #####################

            with GRU_Mel_graph.as_default():
                gru_mel_repr = GRU_Mel_model.predict(mel_spectrogram.reshape([1, 408, 320]))[0]
                song.gru_mel_representation = gru_mel_repr.reshape([5712]).tolist()
                print(gru_mel_repr)

            print('gru mel predicted')

            with LSTM_MFCC_graph.as_default():
                lstm_mfcc_repr = LSTM_MFCC_model.predict(mfcc.reshape([1, 646, 128]))[0]
                song.lstm_mfcc_representation = lstm_mfcc_repr.reshape([5168]).tolist()


            pca_mel_repr = PCA_Mel_model.transform(mel_spectrogram.reshape(1, 130560))
            print('pca mel predicted')
            song.pca_mel_representation = pca_mel_repr.reshape([320]).tolist()
            print('pca mel loaded')
        except:
            song.audio = False





    ##################################### saving text representations ########################

    try:
        tf_idf_repr = retrieve_tf_idf_representation(song)
        print(tf_idf_repr.shape)
        pca_tf_idf_repr = PCA_Tf_idf_model.transform(tf_idf_repr.reshape(1,-1))
        song.pca_tf_idf_representation = pca_tf_idf_repr.reshape([4457]).tolist()
        print('pca tf_idf_represented')

        w2v_repr = retrieve_w2v_representation(song)
        print('w2v predicted')
        if w2v_repr.size != 300:
            song.w2v_representation = numpy.zeros([300]).tolist()
        else:
            song.w2v_representation = w2v_repr.reshape([300]).tolist()
        print('w2v representation')
    except:
        song.lyrics = False

    song.save()
    print('song_saved')

    ######################################################################################
    ######################################################################################


def retrieve_tf_idf_representation(song):
    """
    turns the song lyrics into a Tf-idf vector
    :param song: the song from the database whose lyrics are processed
    :return: Tf-idf vector representation of the newly added song
    """
    lyrics = song.text.lower()
    vector = [w.strip('.,!:?-') for w in lyrics.split(" ")]
    tf_idf_repr = TF_idf_model.transform(vector)
    return tf_idf_repr.toarray()[0]


def retrieve_w2v_representation(song):
    """
        turns the song lyrics into a W2V vector
        :param song: the song from the database whose lyrics are processed
        :return: W2V vector representation of the newly added song
        """
    lyrics = song.text.lower()
    words = [w.strip('.,!:?-') for w in lyrics.split(" ")]
    word_vecs = []
    for word in words:
        try:
            vec = W2V_model[word]
            word_vecs.append(vec)

        except KeyError:
            # Ignore, if the word doesn't exist in the vocabulary
            pass

    # Assuming that document vector is the mean of all the word vectors
    vector = numpy.mean(word_vecs, axis=0)
    return vector


def get_audio_data(song):
    """
    gets a mp3 audio file and converts it into the 15 second audio excerpt
    :param song: the song of which the 15 second audio is created
    :return: returns the waveform information about the 15 second audio.
    """
    sound = AudioSegment.from_mp3(song.link_on_disc)

    if len(sound) < 65000:
        sound = sound.set_channels(1)
        beginning = sound[10000:15000]
        middle = sound[int(len(sound)/2):(len(sound)/2 + 5000)]
        end = sound[-10000:-5000]

    else:
        sound = sound.set_channels(1)
        beginning = sound[20000:25000]
        middle = sound[int(len(sound)/2):(len(sound)/2 + 5000)]
        end = sound[-15000:-10000]

    s = beginning + middle + end
    # play(s)
    print(len(s))
    s.export('temp_wav_file.wav', format='wav')
    y, sr = librosa.load('temp_wav_file.wav')

    return y, sr


def download_song_from_youtube(song):
    """
    downloads the YouTube song into the mp3 file based on the song link from the database.
    :param song: the song whose mp3 file is being downloaded
    :return: None
    """
    url = song.link
    l = song.link
    response = None
    try:
        response = urllib.request.urlopen(url)
    except:
        text_to_search = song.song_name + ' - ' + song.artist
        query = urllib.parse.quote(text_to_search)
        url = "https://www.youtube.com/results?search_query=" + query
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        vid = soup.find_all(attrs={'class': 'yt-uix-tile-link'})[0]
        l = 'https://www.youtube.com' + vid['href']

    ydl_opts = {
        'format': 'bestaudio/best',
        'playlist_items': '0',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': MP3FILES_DIR + "%(title)s.%(ext)s"
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([l])
            try:
                info_dict = ydl.extract_info(l, download=False)
            except:
                pass

            song.link_on_disc =  info_dict.get('title', None) + ".mp3"
            song.audio = True
            song.save()
        except Exception as e:
            song.link_on_disc = ''
            song.audio = False
            song.save()
            print('not saved ok', e)


def retrieve_spectrogram_representation(y, sr):
    """
    transforms the audio time series into a spectrogram
    :param y: audio time series of a particular song
    :param sr: the sampling rate
    :return: a spectrogram from the audio time series
    """
    spectrogram = numpy.abs(librosa.core.stft(y, n_fft=n_fft, hop_length=hop_length))
    return spectrogram


def retrieve_mel_spectrogram_representation(y, sr):
    """
    transforms the audio time series into a mel-spectrogram
    :param y: audio time series of a particular song
    :param sr: the sampling rate
    :return: a mel-spectrogram from the audio time series
    """
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=320, n_fft=4410, hop_length=812)
    return mel_spectrogram


def retrieve_mfcc_representation(y, sr):
    """
   transforms the audio time series into mfccs
   :param y: audio time series of a particular song
   :param sr: the sampling rate
   :return: mfcc from the audio time series
   """
    mfcc = librosa.feature.mfcc(y, sr, n_mfcc=n_mfcc)
    return mfcc
