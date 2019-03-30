from songRecommender.models import Song, Distance
import numpy, youtube_dl, re, urllib.request, librosa, os, scipy.sparse, glob, sklearn.metrics
from bs4 import BeautifulSoup
from rocnikac.settings import MP3FILES_DIR, REPRESENTATIONS_DIR
from pydub import AudioSegment
from rocnikac.settings import TF_idf_model, W2V_model, PCA_Spec_model, \
                              PCA_Mel_model, GRU_Mel_model, GRU_Spec_model, LSTM_Spec_model
from rocnikac.settings import TF_IDF_THRESHOLD, W2V_THRESHOLD, MEL_SPEC_THRESHOLD, MFCC_THRESHOLD, PCA_MEL_THRESHOLD, \
                            PCA_SPEC_THRESHOLD, GRU_MEL_THRESHOLD, GRU_SPEC_THRESHOLD, LSTM_MEL_THRESHOLD
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
    y, sr = get_audio_data(song)

    ######## Saving simple audio representations ###############

    spectrogram = retrieve_spectrogram_representation(y, sr)
    print('got spectrogram')
    print(spectrogram.shape)
    mel_spectrogram = retrieve_mel_spectrogram_representation(y, sr)
    print('got melspectrogram')
    print(mel_spectrogram.shape)
    mfcc = retrieve_mfcc_representation(y, sr)
    print('got mfcc repr')


    # spectrogram_file = REPRESENTATIONS_DIR + '/spectrograms/' + str(song_id) + '_' + str(song.song_name)\
    #                    + '_' + str(song.artist)
    # numpy.save(spectrogram_file, spectrogram)
    #
    # mel_spectrogram_file = REPRESENTATIONS_DIR + '/mel_spectrograms/' + str(song_id) + '_' + str(song.song_name)\
    #                    + '_' + str(song.artist)
    # numpy.save(mel_spectrogram_file, mel_spectrogram)
    #
    # mfcc_file = REPRESENTATIONS_DIR + '/mfcc/' + str(song_id) + '_' + str(song.song_name)\
    #                    + '_' + str(song.artist)
    # numpy.save(mfcc_file, mfcc)

    ##################################### saving text representations ########################

    # tf_idf_repr = retrieve_tf_idf_representation(song)
    w2v_repr = retrieve_w2v_representation(song)
    print('w2v predicted')

    # tf_idf_file = REPRESENTATIONS_DIR + '/tf_idf_vectors/' + str(song_id) + '_' + str(song.song_name)\
    #                    + '_' + str(song.artist)
    # scipy.sparse.save_npz(tf_idf_file, tf_idf_repr)
    #
    # w2v_file = REPRESENTATIONS_DIR + '/w2v_vectors/' + str(song_id) + '_' + str(song.song_name)\
    #                    + '_' + str(song.artist)
    # numpy.save(w2v_file, w2v_repr)

    ############################# Saving more advanced audio representations #####################

    pca_spec_repr = PCA_Spec_model.transform(spectrogram.reshape(1, 900048))
    print('pca spec predicted')
    pca_mel_repr = PCA_Mel_model.transform(mel_spectrogram.reshape(1, 130560))
    print('pca mel predicted')

    # pca_spec_file = REPRESENTATIONS_DIR + '/pca_spectrograms/' + str(song_id) + '_' + str(song.song_name)\
    #                    + '_' + str(song.artist)
    #
    # pca_mel_spec_file = REPRESENTATIONS_DIR + '/pca_mel_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
    #                 + '_' + str(song.artist)
    #
    # numpy.save(pca_spec_file, pca_spec_repr)
    # numpy.save(pca_mel_spec_file, pca_mel_repr)

    gru_spec_repr = GRU_Spec_model.predict(spectrogram.reshape([1, 408, 2206]))
    print('gru spec predicted')
    # gru_spec_file = REPRESENTATIONS_DIR + '/gru_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
    #                 + '_' + str(song.artist)
    # numpy.save(gru_spec_file, gru_spec_repr)

    gru_mel_repr = GRU_Mel_model.predict(mel_spectrogram.reshape([1, 408, 320]))
    print('gru mel predicted')
    # gru_mel_file = REPRESENTATIONS_DIR + '/gru_mel_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
    #                 + '_' + str(song.artist)
    # numpy.save(gru_mel_file, gru_mel_repr)

    lstm_mel_repr = LSTM_Spec_model.predict(mel_spectrogram.reshape([1, 408, 320]))
    print('lstm mel representation predicted')
    # lstm_mel_file = REPRESENTATIONS_DIR + '/lstm_mel_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
    #                 + '_' + str(song.artist)
    # numpy.save(lstm_mel_file, lstm_mel_repr)

    ##################### Saving paths to song ##########################################

    song.spectrogram_representation = spectrogram
    print('spectrogram fitted')
    song.mel_spectrogram_representation = mel_spectrogram
    print('mel_spectrogram fitted')
    song.mfcc_representation = mfcc
    print('mfcc representation fitted')
    # song.tf_idf_representation = tf_idf_repr
    song.w2v_representation = w2v_repr
    print('w2v representation')
    song.pca_spec_representation = pca_spec_repr
    print('pca spectrogram')
    song.pca_mel_representation = pca_mel_repr
    print('pca mel representation')
    song.gru_spec_representation = gru_spec_repr
    print('gru spec repr')
    song.gru_mel_representation = gru_mel_repr
    print('gru mel repr')
    song.lstm_mel_representation = lstm_mel_repr
    print('lstm mel repr')

    song.save()

    ######################################################################################
    ######################################################################################

    mfcc_reprs = load_mfcc_representation()
    print('mfcc loaded')
    # tf_idf_reprs = load_tf_idf_representations()
    w2v_reprs = load_w2v_representations()
    print('w2v loaded')
    pca_mel_reprs = load_mel_pca_representations()
    print('mel reprs loaded')
    pca_spec_reprs = load_pca_representations()
    print('spec reprs loaded')
    gru_mel_reprs = load_gru_mel_representations()
    print('gru mel reprs loaded')
    gru_spec_reprs = load_gru_spec_representations()
    print('gru spec reprs loaded')
    lstm_mel_reprs = load_lstm_mel_representations()
    print('lstm mel reprs loaded')

    save_distances(song, song.get_mfcc_representation(), mfcc_reprs, MFCC_THRESHOLD, "MFCC")
    # save_distances(song, song.get_tf_idf_representation(), tf_idf_reprs, TF_IDF_THRESHOLD, "TF0i-df")
    save_distances(song, song.get_W2V_representation(), w2v_reprs, W2V_THRESHOLD, "W2V")
    save_distances(song, song.get_pca_mel_representation(), pca_mel_reprs, PCA_MEL_THRESHOLD, "PCA_MEL")
    save_distances(song, song.get_pca_spec_representation(), pca_spec_reprs, PCA_SPEC_THRESHOLD, "PCA_SPEC")
    save_distances(song, song.get_gru_spec_representatio(), gru_spec_reprs, GRU_SPEC_THRESHOLD, "GRU_SPEC")
    save_distances(song, song.get_gru_mel_representation(), gru_mel_reprs, GRU_MEL_THRESHOLD, "GRU_MEL")
    save_distances(song, song.get_lstm_mel_representation(), lstm_mel_reprs, LSTM_MEL_THRESHOLD, "LSTM_MEL")

def load_mfcc_representation():
    representations = numpy.empty(Song.objects.all().count(), 82688)
    i = 0
    for song in Song.objects.all():
        representations[i] = song.get_mfcc_representation()
        print(i, 'mfcc')
        i = i + 1
    return representations


def load_pca_representations():
    representations = numpy.empty(Song.objects.all().count(), 320)
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_pca_spec_representation()
        print(i, 'pca')
        i = i + 1
    return representations


def load_mel_pca_representations():
    representations = numpy.empty(Song.objects.all().count(), 320)
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_pca_mel_representation()
        print(i, 'mel pca')
        i = i + 1
    return representations


def load_gru_mel_representations():
    representations = numpy.empty(Song.objects.all().count(), 32640)
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_gru_mel_representation()
        print(i, 'gru mel')
        i = i + 1
    return representations


def load_gru_spec_representations():
    representations = numpy.empty(Song.objects.all().count(), 128520)
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_gru_spec_representation()
        print(i, 'gru spec')
        i = i + 1
    return representations


def load_lstm_mel_representations():
    representations = numpy.empty(Song.objects.all().count(), 32640)
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_lstm_mel_representation()
        print(i, 'lstm mel')
        i = i + 1
    return representations


# def load_tf_idf_representations():
#     representations = numpy.empty(Song.objects.all().count(), )
#     i = 0
#     for song in Song.objects.all().order_by('id'):
#         representations[i] = song.get_lstm_mel_representation()
#         i = i + 1
#     return representations


def load_w2v_representations():
    representations = numpy.empty(Song.objects.all().count(), 300)
    i = 0
    for song in Song.objects.all().order_by('id'):
        representations[i] = song.get_lstm_mel_representation()
        print(i, 'w2v')
        i = i+1

    return representations


def save_distances(song, song_representation, representations, threshold, distance_type):

    try:
        distances = sklearn.metrics.pairwise.cosine_similarity(song_representation.reshape(1,-1), representations)

        for song_2 in Song.objects.all().order_by('id'):
            if distances[song_2.id] > threshold and (song.id != song_2.id):
                dist_1 = Distance(song_1=song, song_2=song_2, distance_Type=distance_type, distance=distances[song_2.id])
                dist_2 = Distance(song_1=song_2, song_2=song, distance_Type=distance_type, distance=distances[song_2.id])
                dist_1.save()
                dist_2.save()
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
        ydl.download([l])
        info_dict = ydl.extract_info(l, download=False)
        song.link_on_disc = MP3FILES_DIR + info_dict.get('title', None) + ".mp3"
        song.save()


def retrieve_spectrogram_representation(y, sr):
    spectrogram = numpy.abs(librosa.core.stft(y, n_fft=n_fft, hop_length=hop_length))
    return spectrogram


def retrieve_mel_spectrogram_representation(y, sr):
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=320, n_fft=4410, hop_length=812)
    return mel_spectrogram


def retrieve_mfcc_representation(y, sr):
    mfcc = librosa.feature.mfcc(y, sr, n_mfcc=n_mfcc)
    return mfcc
