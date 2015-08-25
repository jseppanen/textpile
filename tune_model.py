
import sqlite3
from update_relevance import query_train
from model import crossvalidate, tune_hyper, extract_words

#param = dict(regu=0.01, bg_weight=0.03) # 0.575
#param = dict(regu=1e-6, bg_weight=1e-3) # 0.796
#param = dict(regu=3e-6, bg_weight=1e-5) # 0.785
#param = dict(regu=1e-7, bg_weight=1e-2) # 0.782
#param = dict(regu=1e-8, bg_weight=1e-5) # 0.825
#param = dict(regu=1e-8, bg_weight=1e-4) # 0.822

conn = sqlite3.connect('data/textpile.db')
docs, labels = query_train(conn)

#feas = map(extract_words, docs)
#print crossvalidate(feas, labels, param)

print tune_hyper(docs, labels)
