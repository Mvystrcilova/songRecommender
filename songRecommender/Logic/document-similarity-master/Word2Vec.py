from gensim.models.keyedvectors import KeyedVectors
model_path = './data/GoogleNews-vectors-negative300.bin'
w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=True)

from .DocSim import DocSim
ds = DocSim(w2v_model)

source_doc = 'how to delete an invoice'
target_docs = ['delete a invoice', 'how do i remove an invoice', 'purge an invoice']

# This will return 3 target docs with similarity score
sim_scores = ds.calculate_similarity(source_doc, target_docs)

print(sim_scores)
