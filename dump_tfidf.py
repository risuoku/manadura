from mkp.analysis import (
    get_document_by_aid,
    verb_tokenizer,
    list_tfidf_scores,
)
import pickle
import os
from mkp import settings

results = list_tfidf_scores()


with open(os.path.join(settings.STORAGE_DIR, 'tfidf_results.pickle'), 'wb') as f:
    pickle.dump(results, f)
