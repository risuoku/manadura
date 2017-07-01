import pickle
from mkp.analysis import list_high_score_words

#with open('storage/tfidf_results.pickle', 'rb') as f:
#    a = pickle.load(f)

a = list_high_score_words()
for i in a:
    print(i)
