from songRecommender.models import Song
import numpy, youtube_dl, re, urllib.request, librosa, os, scipy.sparse
from bs4 import BeautifulSoup
from rocnikac.settings import MP3FILES_DIR, REPRESENTATIONS_DIR
from pydub import AudioSegment
from rocnikac.settings import TF_idf_model, W2V_model, PCA_Spec_model, \
                              PCA_Mel_model, GRU_Mel_model, GRU_Spec_model, LSTM_Spec_model
from rocnikac.settings import TF_IDF_THRESHOLD, W2V_THRESHOLD, MEL_SPEC_THRESHOLD, MFCC_THRESHOLD, PCA_MEL_THRESHOLD, \
                            PCA_SPEC_THRESHOLD, GRU_MEL_THRESHOLD, GRU_SPEC_THRESHOLD, LSTM_MEL_THRESHOLD
from rocnikac.settings import n_fft, hop_length, n_mfcc, n_mels

def save_all_representations_and_distances(song_id):

    song = Song.objects.get(pk=song_id)
    y, sr = get_audio_data(song)

    ######## Saving simple audio representations ###############

    spectrogram = retrieve_spectrogram_representation(y, sr)
    mel_spectrogram = retrieve_mel_spectrogram_representation(y, sr)
    mfcc = retrieve_mfcc_representation(y, sr)

    spectrogram_file = REPRESENTATIONS_DIR + '/spectrograms/' + str(song_id) + '_' + str(song.song_name)\
                       + '_' + str(song.artist)
    numpy.save(spectrogram_file, spectrogram)

    mel_spectrogram_file = REPRESENTATIONS_DIR + '/mel_spectrograms/' + str(song_id) + '_' + str(song.song_name)\
                       + '_' + str(song.artist)
    numpy.save(mel_spectrogram_file, mel_spectrogram)

    mfcc_file = REPRESENTATIONS_DIR + '/mfcc/' + str(song_id) + '_' + str(song.song_name)\
                       + '_' + str(song.artist)
    numpy.save(mfcc_file, mfcc)

    ########## saving text representations ########################

    tf_idf_repr = retrieve_tf_idf_representation(song)
    w2v_repr = retrieve_w2v_representation(song)

    tf_idf_file = REPRESENTATIONS_DIR + '/tf_idf_vectors/' + str(song_id) + '_' + str(song.song_name)\
                       + '_' + str(song.artist)
    scipy.sparse.save_npz(tf_idf_file, tf_idf_repr)

    w2v_file = REPRESENTATIONS_DIR + '/w2v_vectors/' + str(song_id) + '_' + str(song.song_name)\
                       + '_' + str(song.artist)
    numpy.save(w2v_file, w2v_repr)

    ############## Saving more advanced audio representations #############

    pca_spec_repr = PCA_Spec_model.transform(spectrogram.reshape(1, 900048))
    pca_mel_repr = PCA_Mel_model.transform(mel_spectrogram.reshape(1, 130560))

    pca_spec_file = REPRESENTATIONS_DIR + '/pca_spectrograms/' + str(song_id) + '_' + str(song.song_name)\
                       + '_' + str(song.artist)

    pca_mel_spec_file = REPRESENTATIONS_DIR + '/pca_mel_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
                    + '_' + str(song.artist)

    numpy.save(pca_spec_file, pca_spec_repr)
    numpy.save(pca_mel_spec_file, pca_mel_repr)

    gru_spec_repr = GRU_Spec_model.transfrom(spectrogram)
    gru_spec_file = REPRESENTATIONS_DIR + '/gru_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
                    + '_' + str(song.artist)
    numpy.save(gru_spec_file, gru_spec_repr)

    gru_mel_repr = GRU_Mel_model.transfrom(mel_spectrogram)
    gru_mel_file = REPRESENTATIONS_DIR + '/gru_mel_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
                    + '_' + str(song.artist)
    numpy.save(gru_mel_file, gru_mel_repr)

    lstm_mel_repr = GRU_Spec_model.transfrom(mel_spectrogram)
    lstm_mel_file = REPRESENTATIONS_DIR + '/lstm_mel_spectrograms/' + str(song_id) + '_' + str(song.song_name) \
                    + '_' + str(song.artist)
    numpy.save(lstm_mel_file, lstm_mel_repr)

    ######################################################################################
    ######################################################################################


















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
        middle = sound[30000:35000]
        end = sound[-10000:-5000]

    else:
        sound = sound.set_channels(1)
        beginning = sound[20000:25000]
        middle = sound[60000:65000]
        end = sound[-15000:-10000]

    s = beginning + middle + end
    s.export('temp_wav_file.wav', format='wav')
    y, sr = librosa.load('temp_wav_file.wav')

    return y, sr


def download_song_from_youtube(song):
    url = song.link
    try:
        response = urllib.request.urlopen(url)
    except:
        text_to_search = song.song_name + ' - ' + song.artist
        query = urllib.parse.quote(text_to_search)
        url = "https://www.youtube.com/results?search_query=" + query
        try:
            response = urllib.request.urlopen(url)
        except:
            return None
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    vid = soup.find_all(attrs={'class':'yt-uix-tile-link'})[0]
    l = 'https://www.youtube.com' + vid['href']
    name = text_to_search + ".mp3"

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
    spectrogram = numpy.abs(librosa.core.stft(y, n_fft=n_fft,hop_length=hop_length))
    return spectrogram

def retrieve_mel_spectrogram_representation(y, sr):
    mel_spectrogram = librosa.feature.melspectrogram(y, sr, n_fft=n_fft, hop_length=hop_length)
    return mel_spectrogram

def retrieve_mfcc_representation(y, sr):
    mfcc = librosa.feature.mfcc(y, sr,n_mfcc=n_mfcc)
    return mfcc
