import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import pickle
import dataProcess as d

class BM25(object):
    def __init__(self, b=0.75, k1=1.6):
        self.vectorizer = TfidfVectorizer(norm=None, smooth_idf=False, ngram_range=(1, 3), preprocessor=d.preProcess)
        self.b = b
        self.k1 = k1

    def fit(self, X):
        """ Fit IDF to documents X """
        self.vectorizer.fit(X)
        y = super(TfidfVectorizer, self.vectorizer).transform(X)
        self.X = y
        self.avdl = y.sum(1).mean()

    def transform(self, q):
        """ Calculate BM25 between query q and documents X """
        b, k1, avdl = self.b, self.k1, self.avdl

        len_X = self.X.sum(1).A1

        q, = super(TfidfVectorizer, self.vectorizer).transform([q])

        assert sparse.isspmatrix_csr(q)
        # convert to csc for better column slicing
        X = self.X.tocsc()[:, q.indices]
        denom = X + (k1 * (1 - b + b * len_X / avdl))[:, None]
        # idf(t) = log [ n / df(t) ] + 1 in sklearn, so it need to be coneverted
        # to idf(t) = log [ n / df(t) ] with minus 1
        idf = self.vectorizer._tfidf.idf_[None, q.indices] - 1.
        numer = X.multiply(np.broadcast_to(idf, X.shape)) * (k1 + 1)
        return (numer / denom).sum(1).A1

if __name__ == '__main__':
    parsed_data = pickle.load(open('resources/cleaned_df.pkl', 'rb'))
    bm25_ingred = BM25()
    bm25_ingred.fit(parsed_data['cleaned_ingredients'])
    pickle.dump(bm25_ingred, open('models/bm25_ingred.pkl', 'wb'))

    bm25_title = BM25()
    bm25_title.fit(parsed_data['title'])
    pickle.dump(bm25_title, open('models/bm25_title.pkl', 'wb'))

#test search by ingredient
import pandas as pd
score = bm25_ingred.transform('teriyaki')
df_bm = pd.DataFrame({'bm25': list(score), 'title': list(parsed_data['title']), 'ingredients': list(parsed_data['ingredients']), 'instructions': list(parsed_data['instructions']), 'image_name': list(parsed_data['image_name']),}).nlargest(columns='bm25', n=10)
df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
df_bm = df_bm.drop(columns='bm25', axis=1)
df_bm


score = bm25_title.transform('teriyaki')
df_bm = pd.DataFrame({'bm25': list(score), 'title': list(parsed_data['title']), 'ingredients': list(parsed_data['ingredients']), 'instructions': list(parsed_data['instructions']), 'image_name': list(parsed_data['image_name']),}).nlargest(columns='bm25', n=10)
df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
df_bm = df_bm.drop(columns='bm25', axis=1)
df_bm