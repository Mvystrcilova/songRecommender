from gensim.models.keyedvectors import KeyedVectors
import pandas
from songRecommender.Logic.DocSim import DocSim

# '/Users/m_vys/Documents/matfyz/rocnikac/songs_with_lyrics','r'
def get_all_words():
    words = []
    with open('/Users/m_vys/Documents/matfyz/rocnikac/djangoApp/rocnikac/songRecommender/Logic/Recommender.py') as f:
        for line in f:
            for word in line.split():
                words.append(word.lower())
    final_list = list(set(words))

    return final_list


def get_w2v_model(all_words, w2v_model):
    model = {}
    h = open('w2v_subset2', 'a', encoding='utf-8')
    for word in all_words:
        try:
            vec = w2v_model[word]
            model[word] = vec
        except KeyError:
            pass
    for word in model.keys():
        h.write(word + ';')
        vector = str(w2v_model[word])
        h.write('\"' + vector + '\"' + '\n')



model_path = '/Users/m_vys/Documents/matfyz/rocnikac/djangoApp/rocnikac/songRecommender/Logic/GoogleNews-vectors-negative300.bin'
_w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=True, limit=100000)
_all_words = get_all_words()
get_w2v_model(_all_words, _w2v_model)
