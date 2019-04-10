from songRecommender.models import Song, Distance
import numpy, youtube_dl, re, urllib.request, librosa, os, scipy.sparse, glob, sklearn.metrics
from bs4 import BeautifulSoup
from rocnikac.settings import MP3FILES_DIR
from pydub import AudioSegment
from rocnikac.settings import GRU_Mel_graph, LSTM_Mel_graph
from keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler

from rocnikac.settings import TF_idf_model, W2V_model, PCA_Spec_model, \
                              PCA_Mel_model, GRU_Mel_model, LSTM_Mel_model
from rocnikac.settings import TF_IDF_THRESHOLD, W2V_THRESHOLD, LSTM_MFCC_THRESHOLD, GRU_MFCC_THRESHOLD, PCA_MEL_THRESHOLD, \
                            PCA_SPEC_THRESHOLD, GRU_MEL_THRESHOLD, LSTM_SPEC_THRESHOLD, LSTM_MEL_THRESHOLD
from rocnikac.settings import n_fft, hop_length, n_mfcc, n_mels

import re
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def save_all_representations_and_distances(song_id):

    song = Song.objects.get(pk=song_id)
    download_song_from_youtube(song)
    scaler = MinMaxScaler()
    if song.link_on_disc != '':
        y, sr = get_audio_data(song)

        ######## Saving simple audio representations ###############

        spectrogram = retrieve_spectrogram_representation(y, sr)
        spectrogram = scaler.fit_transform(spectrogram.reshape([1, 900048]))
        spectrogram = spectrogram.reshape([1, 408, 2206])
        print('got spectrogram')
        print(spectrogram.shape)
        mel_spectrogram = retrieve_mel_spectrogram_representation(y, sr)
        mel_spectrogram = scaler.fit_transform(mel_spectrogram.reshape([1, 130560]))
        mel_spectrogram = mel_spectrogram.reshape([1, 408, 320])
        print('got melspectrogram')
        print(mel_spectrogram.shape)
        mfcc = retrieve_mfcc_representation(y, sr)
        mfcc = scaler.fit_transform(mfcc.reshape([1, 82688]))
        mfcc = mfcc.reshape([1, 646, 128])
        print('got mfcc repr')

        ############################# Saving more advanced audio representations #####################

        pca_spec_repr = PCA_Spec_model.transform(scaler.fit_transform(spectrogram.reshape(1, 900048)))
        print('pca spec predicted')
        pca_mel_repr = PCA_Mel_model.transform(mel_spectrogram.reshape(1, 130560))
        print('pca mel predicted')

        with GRU_Mel_graph.as_default():
            gru_mel_repr = GRU_Mel_model.predict(scaler.fit_transform(mel_spectrogram.reshape([1, 408, 320])))[0]
            song.gru_mel_representation = gru_mel_repr.reshape([1, 5712]).tolist()
            print(gru_mel_repr)

        print('gru mel predicted')
        with LSTM_Mel_graph.as_default():
            lstm_mel_repr = LSTM_Mel_model.predict(mel_spectrogram.reshape([1, 408, 320]))[0]
            song.lstm_mel_representation = lstm_mel_repr.reshape([1, 5712]).tolist()
            print(lstm_mel_repr)
        print('lstm mel representation predicted')

         ##################### Saving paths to song ##########################################

        # song.spectrogram_representation = spectrogram
        # print(spectrogram)
        # print('spectrogram fitted')
        # song.mel_spectrogram_representation = mel_spectrogram
        # print(mel_spectrogram)
        # print('mel_spectrogram fitted')
        # song.mfcc_representation = mfcc
        # print(mfcc)
        # print('mfcc representation fitted')
        # song.tf_idf_representation = tf_idf_repr

        print('pca spectrogram')
        song.pca_spec_representation = pca_spec_repr.tolist()
        print(pca_spec_repr)
        print('pca spec representation')
        # song.gru_spec_representation = gru_spec_repr
        # print('gru spec repr')


        # gru_mfcc_reprs = load_gru_mfcc_representation()
        # print('gru mfcc loaded')
        # save_distances(song, song.get_gru_mfcc_representation(), gru_mfcc_reprs, GRU_MFCC_THRESHOLD, "MFCC")
        # print('gru mfcc_distances_saved')
        # gru_mfcc_reprs = None
        #
        # lstm_mfcc_reprs = load_lstm_mfcc_representation()
        # print('lstm mfcc loaded')
        # save_distances(song, song.get_lsmt_mfcc_representation(), lstm_mfcc_reprs, LSTM_MFCC_THRESHOLD, "MFCC")
        # print('lstm mfcc_distances_saved')
        # lstm_mfcc_reprs = None
        song.pca_mel_representation = pca_mel_repr.tolist()
        pca_mel_reprs = load_mel_pca_representations()
        print('mel reprs loaded')
        save_distances(song, song.get_pca_mel_representation(), pca_mel_reprs, PCA_MEL_THRESHOLD, "PCA_MEL")
        print('pca_mel distances saved')
        pca_mel_reprs = None

        pca_spec_reprs = load_pca_representations()
        print('spec reprs loaded')
        save_distances(song, song.get_pca_spec_representation(), pca_spec_reprs, PCA_SPEC_THRESHOLD, "PCA_SPEC")
        print('pca spec distances save')
        pca_spec_reprs = None

        gru_mel_reprs = load_gru_mel_representations()
        print('gru mel reprs loaded')
        save_distances(song, song.get_gru_mel_representation(), gru_mel_reprs, GRU_MEL_THRESHOLD, "GRU_MEL")
        print('gru mel distances saved')
        gru_mel_reprs = None

        # gru_spec_reprs = load_gru_spec_representations()
        # print('gru spec reprs loaded')
        # save_distances(song, song.get_gru_spec_representatio(), gru_spec_reprs, GRU_SPEC_THRESHOLD, "GRU_SPEC")

        lstm_mel_reprs = load_lstm_mel_representations()
        print('lstm mel reprs loaded')
        save_distances(song, song.get_lstm_mel_representation(), lstm_mel_reprs, LSTM_MEL_THRESHOLD, "LSTM_MEL")
        print('lstm mel distances saved')
        lstm_mel_reprs = None

    ##################################### saving text representations ########################

    # tf_idf_repr = retrieve_tf_idf_representation(song)
    w2v_repr = retrieve_w2v_representation(song)
    print('w2v predicted')

    song.w2v_representation = w2v_repr.tolist()
    print('w2v representation')
    # song.pca_spec_representation = pca_spec_repr

    song.save()
    print('song_saved')

    ######################################################################################
    ######################################################################################

    w2v_reprs = load_w2v_representations()
    print('w2v loaded')
    save_distances(song, song.get_W2V_representation(), w2v_reprs, W2V_THRESHOLD, "W2V")
    w2v_reprs = None

    tf_idf_reprs = load_tf_idf_representations()
    print('tf_idf loaded')
    save_distances(song, song.get_tf_idf_representation(), tf_idf_reprs, TF_IDF_THRESHOLD, "TF0i-df")
    tf_idf_reprs = None






def load_gru_mfcc_representation():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 5248])
    i = 0
    for song in Song.objects.all():
        representations[i] = song.get_mfcc_representation()
        print(i, 'gru_mfcc')
        i = i + 1
    return representations

def load_lstm_mfcc_representation():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 5248])
    i = 0
    for song in Song.objects.all():
        representations[i] = song.get_mfcc_representation()
        print(i, 'lstm_mfcc')
        i = i + 1
    return representations


def load_pca_representations():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 1106])
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_pca_spec_representation()
        print(i, 'pca')
        i = i + 1
    return representations


def load_mel_pca_representations():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 5717])
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_pca_mel_representation()
        print(i, 'mel pca')
        i = i + 1
    return representations


def load_gru_mel_representations():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 5712])
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_gru_mel_representation()
        print(i, 'gru mel')
        i = i + 1
    return representations


def load_gru_spec_representations():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 128520])
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_gru_spec_representation()
        print(i, 'gru spec')
        i = i + 1
    return representations


def load_lstm_mel_representations():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 5712])
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_lstm_mel_representation()
        print(i, 'lstm mel')
        i = i + 1
    return representations

def load_tf_idf_representations(chunk_size):
    count = Song.objects.all().count()
    representations = numpy.empty([chunk_size, 40165])
    i = 0
    for song in Song.objects.all().order_by('id'):
        if (i % chunk_size == 0) and (i != 0):
            representations[i] = song.get_tf_idf_representation()
            print(i, 'tf-idf')
        elif i > count:
            representations = representations[:i]
        i = i + 1
    return representations



def load_w2v_representations():
    count = Song.objects.all().count()
    representations = numpy.empty([count, 300])
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_lstm_mel_representation()
        print(i, 'w2v')
        i = i+1

    return representations


def save_distances(song, song_representation, representations, threshold, distance_type):

    try:
        distances = sklearn.metrics.pairwise.cosine_similarity(song_representation.reshape(1,-1), representations)
        i = 0
        for song_2 in Song.objects.all().order_by('id'):
            if distances[i] > threshold and (song.id != song_2.id):
                dist_1 = Distance(song_1=song, song_2=song_2, distance_Type=distance_type, distance=distances[song_2.id])
                dist_2 = Distance(song_1=song_2, song_2=song, distance_Type=distance_type, distance=distances[song_2.id])
                dist_1.save()
                dist_2.save()
                print('distance', song, song_2, 'saved')
            i = i+1
    except:
        pass

    print('distances', distance_type, 'saved')


def retrieve_tf_idf_representation(song):
    lyrics = song.text.lower()
    vector = [w.strip('.,!:?-') for w in lyrics.split(" ")]
    tf_idf_repr = TF_idf_model.transform(vector)
    return tf_idf_repr


def retrieve_w2v_representation(song):
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
    # PS: There are other & better ways to do it.
    vector = numpy.mean(word_vecs, axis=0)
    return vector


def get_audio_data(song):
    sound = AudioSegment.from_mp3(song.link_on_disc)

    if len(sound) < 65000:
        sound = sound.set_channels(1)
        beginning = sound[10000:15000]
        middle = sound[int(len(sound)/2):(len(sound)/2 + 5000)]
        end = sound[-10000:-5000]

    else:
        sound = sound.set_channels(1)
        beginning = sound[20000:25000]
        middle = sound[60000:65000]
        end = sound[-15000:-10000]

    s = beginning + middle + end
    print(len(s))
    s.export('temp_wav_file.wav', format='wav')
    y, sr = librosa.load('temp_wav_file.wav')

    return y, sr


def download_song_from_youtube(song):
    url = song.link
    l = song.link
    response = None
    regex = re.compile('[^A-Za-z0-9 -]')
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
            info_dict = ydl.extract_info(l, download=False)

            song.link_on_disc = MP3FILES_DIR + info_dict.get('title', None) + ".mp3"
            song.save()
            print('song_saved_ok', song.link_on_disc)
        except Exception as e:
            song.link_on_disc = ''
            song.save()
            print('not saved ok', e)


def retrieve_spectrogram_representation(y, sr):
    spectrogram = numpy.abs(librosa.core.stft(y, n_fft=n_fft, hop_length=hop_length))
    return spectrogram


def retrieve_mel_spectrogram_representation(y, sr):
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=320, n_fft=4410, hop_length=812)
    return mel_spectrogram


def retrieve_mfcc_representation(y, sr):
    mfcc = librosa.feature.mfcc(y, sr, n_mfcc=n_mfcc)
    return mfcc
