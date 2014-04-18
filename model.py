from __future__ import division
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import StratifiedKFold
from scipy import sparse
from collections import defaultdict
import re
import numpy as np
import sys

def train(docs, labels, regu=1, bg_weight=.1):
    '''
    :param docs: iterator of (title, body) pairs
    :param labels: integer labels for docs (0 is weakly-negative)
    :return: model
    '''
    num_topics=50
    feas = map(extract_words,  docs)
    labels = np.array(list(labels), dtype=int)
    idf=train_idf(feas)
    X,vocab=extract_feas(feas, idf)
    #lda=train_lda(X, vocab, num_topics)
    #X=transform_lda(X, lda)
    # set up sample weights
    weights = balance_weights(labels, bg_weight)
    labels=labels.copy()
    labels[labels == 0] = 1
    model=SGDClassifier(loss='log',
                        alpha=regu/len(labels),
                        fit_intercept=True,
                        n_iter=100,
                        shuffle=True)
    model.fit(X, labels, sample_weight=weights)
    #print accuracy(labels, model.predict(X))
    return dict(idf=idf, logreg=model, lda=None)

def predict(model, docs, doc_ids, topk=9999):
    '''
    :param docs: iterator of (title, body) pairs
    :return: list of top ranked (doc_id, label, score, keywords)
    '''
    feas = map(extract_words,  docs)
    X,vocab=extract_feas(feas, model['idf'])
    #X=transform_lda(X, model['lda'])
    pp=model['logreg'].predict_proba(X)
    pred_labels = np.argmax(pp, 1)
    pred_labels = model['logreg'].classes_[pred_labels]
    # return all scores for "good" class
    assert model['logreg'].classes_[1] == 2
    pred_scores = pp[:,1]
    # find top items
    ii = np.argsort(-pred_scores)[:topk]
    doc_ids = list(doc_ids)
    doc_ids = [doc_ids[i] for i in ii]
    pred_labels = pred_labels[ii]
    pred_scores = pred_scores[ii]
    # attach top-5 strongest keywords for each item
    fea_scores = X[ii].multiply(model['logreg'].coef_).getA()
    fea_ids = np.argsort(-fea_scores, axis=1)[:,:5]
    def mkeyword(f):
        if f[0] == 'desc':
            return f[1]
        return '%s:%s' % f
    keywords = [[{'keyword': mkeyword(vocab[j]),
                  'score': round(fea_scores[i,j]*1000)}
                 for j in jj]
                for i,jj in enumerate(fea_ids)]
    return zip(doc_ids, pred_labels, pred_scores, keywords)

def tune_hyper(docs, labels):
    feas = map(extract_words,  docs)
    labels = list(labels)
    best_param = {}
    best_accuracy = -1.0
    num_topics=50
    for bg_weight in [1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1,
                      1e0, 3e0, 1e1, 3e1]:
        for regu in [1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4,
                     1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1]:
            param = dict(bg_weight=bg_weight,
                         regu=regu)
            acc = crossvalidate(feas, labels, param)
            print '| %g %g %.4f' % (bg_weight, regu, acc),
            if acc > best_accuracy:
                best_param = param
                best_accuracy = acc
                print '*'
            else:
                print
            sys.stdout.flush()
    return best_param

def crossvalidate(feas, labels, param):
    labels = np.array(list(labels), dtype=int)
    accs = []
    for train_ids, valid_ids in StratifiedKFold(labels, 10):
        idf=train_idf([feas[i] for i in train_ids])
        X,vocab=extract_feas(feas, idf)
        #lda=train_lda(X, vocab, num_topics)
        #X=transform_lda(X, lda)
        labels_train = labels[train_ids].copy()
        weights = balance_weights(labels_train, param['bg_weight'])
        labels_train[labels_train == 0] = 1
        model=SGDClassifier(loss='log',
                            alpha=param['regu']/len(labels_train),
                            fit_intercept=True,
                            shuffle=True, n_iter=50)
        model.fit(X[train_ids], labels_train, sample_weight=weights)
        pp = model.predict_proba(X[valid_ids])
        pred_labels = np.argmax(pp, 1)
        pred_labels = model.classes_[pred_labels]
        #a=accuracy(labels[valid_ids], pred_labels, 1)
        # return all scores for "good" class
        assert model.classes_[1] == 2
        pred_scores = pp[:,1]
        a=avg_precision(labels[valid_ids], pred_scores)
        print '%.2f' % a,
        accs.append(a)
    return np.mean(accs)

def balance_weights(labels, bg_weight):
    '''0: weakly-negative "background" class
       1: negative class
       2: positive class'''
    # balance weights by inverse counts
    weights = np.ones(len(labels))
    z = 0.0
    ws = {0:bg_weight, 1:1.0, 2:1.0}
    for label, count in enumerate(np.bincount(labels)):
        if count:
            weights[labels==label] = ws[label] / count
            z += ws[label]
    weights *= len(labels) / z
    return weights

def accuracy(true_labels, pred_labels, false_negative_weight=100):
    correct = (true_labels == pred_labels)
    weights = np.ones(len(correct))
    weights[(true_labels == 2) * (pred_labels == 1)] = false_negative_weight
    # average accuracy across classes
    acc = []
    for label in set(true_labels):
        if label == 0:
            continue
        ids = (true_labels == label)
        a = sum(weights[ids] * correct[ids]) / sum(weights[ids])
        acc.append(a)
    return np.mean(acc)

def avg_precision(true_labels, pred_scores):
    # ignore unknown documents
    ids = (true_labels > 0)
    true_labels = true_labels[ids]
    pred_scores = pred_scores[ids]
    ranking = np.argsort(-pred_scores)
    ranks = np.zeros(len(ranking))
    ranks[ranking] = np.arange(len(ranking))
    ranks = ranks[true_labels == 2]
    ranks.sort()
    ap = 0
    for n,r in enumerate(ranks):
        ap += (n+1.0) / (r+1.0)
    ap /= len(ranks)
    return ap

toks_re = re.compile(r'\w+', re.UNICODE)
def toks(txt):
    words = toks_re.findall(txt.lower())
    words = [w for w in words if w[0] not in '0123456789']
    def stem(word):
        if len(word) >= 8:
            return word[:-3] + '___'
        return word
    return map(stem, words)

# http://stackoverflow.com/questions/5553410/regular-expression-match-a-sentence#5553924
# Match a sentence ending in punctuation or EOS.
sents_re = re.compile(
    # First char is non-punct, non-ws
    "[^.!?\\s]" +
    # Greedily consume up to punctuation.
    "[^.!?]*" +
    # Group for unrolling the loop.
    "(?:" +
    # (special) inner punctuation ok if
    "  [.!?]" +
    # not followed by ws or EOS.
    "  (?!['\"]?\\s|$)" +
    # Greedily consume up to punctuation.
    "  [^.!?]*" +
    # Zero or more (special normal*)
    ")*" +
    # Optional ending punctuation.
    "[.!?]?" +
    # Optional closing quote.
    "['\"]?" +
    "(?=\\s|$)", 
    re.MULTILINE)
def sentences(txt):
    sents = sents_re.findall(txt)
    sents = [s for s in sents if s]
    return sents

def extract_words(doc):
    feas = defaultdict(float)
    for w in toks(doc[0]):
        feas['title', w] += 1
    for w in toks(doc[1]):
        feas['desc', w] += 1
    return feas

def train_idf(feas):
    # compute document frequency
    df = defaultdict(set)
    for i,ws in enumerate(feas):
        for w in ws:
            df[w].add(i)
    df = [(w, len(df[w])) for w in df]
    # find most popular tokens
    df.sort(key=lambda x:-x[1])
    stopwords = set(w for w,f in df[:200])
    # FIXME prune 1-2 letter words
    # FIXME prune words only appearing in a single doc
    idf = dict((w, np.log(len(feas)/f)) for w,f in df if w not in stopwords)
    return idf

def extract_feas(docs, idf):
    vocab = list(idf)
    wordids = dict((w,i) for i,w in enumerate(vocab))
    X=[(i, wordids[w], ws[w]/sum(ws.values())*idf[w])
       for i,ws in enumerate(docs) for w in ws
       if w in wordids]
    ii,jj,xx = zip(*X)
    X=sparse.coo_matrix((xx, (ii, jj)), shape=[len(docs), len(vocab)])
    X=X.tocsr()
    return X, vocab

def train_lda(X, vocab, num_topics=100):
    import warnings
    # suppress a million of these:
    #   score += numpy.sum(cnt * logsumexp(Elogthetad + Elogbeta[:, id]) for id, cnt in doc)
    # /usr/local/lib/python2.7/dist-packages/gensim/models/ldamodel.py:634: DeprecationWarning: using a non-integer number instead of an integer will result in an error in the future
    warnings.simplefilter('ignore')
    import gensim
    # shuffle for online LDA
    ii=np.random.permutation(X.shape[0])
    xc=gensim.matutils.Sparse2Corpus(X[ii].T)
    lda=gensim.models.ldamodel.LdaModel(xc, num_topics=num_topics,
                                        chunksize=300, passes=5,
                                        id2word=dict(enumerate(vocab)))
    return lda

def transform_lda(X, lda):
    XX = np.zeros((X.shape[0], lda.num_topics))
    for i in range(X.shape[0]):
        for j,w in lda[zip(X[i].indices, X[i].data)]:
            XX[i,j] = w
    return XX
