"""
keyword_expansion
=================

Data-driven expansion of keywords [experimental]
"""

from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import numpy as np


def matrix_fraction(X):
    '''Convenience method for calculating the relative fraction of 
    each column sum with respect to the total matrix sum.
    Required for JLH scoring.

    Args:
        X: A numpy-like matrix (m x n)
    Returns:
        Y: A numpy-like array (m x 1).
    '''
    _sum = X.sum(axis=0)
    return _sum/(_sum.sum())


def jlh(foreground, background):
    a = matrix_fraction(foreground)
    b = matrix_fraction(background)
    jlh_scores = np.asarray(a / b) * np.asarray(a - b)
    if len(jlh_scores.shape) > 1:
        jlh_scores = jlh_scores[0]
    return list(jlh_scores)


# Note: consider the following for cv_kwargs
# max_df=0.95, min_df=2,
# max_features=500,
# binary=False, stop_words='english'
def keyword_expansion(docs, search_terms, threshold=0.3,
                      n_unkeywords=10, **cv_kwargs):
    """
    Generate an expanded set of keywords related to search terms in a corpus
    of documents, based on the JLH score.

    Args:
        docs (list): List of tokenized documents (each doc is a list).
        search_terms (str): Space delimited set of terms to expand.
        threshold (float): Select expanded keywords which have a JLH score
                           equal to the threshold times the mininum JLH score of
                           the search terms.
        n_unkeywords (int): Number of terms least related to the search terms.
    Returns:
        keywords (list): List of keywords related to the search terms
        unkeywords (list): List of terms least related to the search terms.
    """

    search_terms = search_terms.split()
    # Scan the documents for the search term, and prepare the docs for analysis
    search_docs = [idx for idx, doc in enumerate(docs)
                   if all(term in doc for term in search_terms)]
    docs = [' '.join(doc) for doc in docs]
    search_docs = [docs[idx] for idx in search_docs]

    # Create count vectors of the foreground and background
    vectorizer = CountVectorizer(**cv_kwargs)
    background = vectorizer.fit_transform(docs)
    foreground = vectorizer.transform(search_docs)
    features = vectorizer.get_feature_names()

    # Calculate significant related text scores
    jlh_scores = jlh(foreground, background)

    # Extract keywords
    scores = {feat: score for feat, score in zip(features, jlh_scores)}
    min_score = max(scores[term] for term in search_terms)
    significant_score = min_score*threshold
    keywords = {feat: score for feat, score in scores.items()
                if score > significant_score}

    # Extract unkeywords
    unscores = {feat: -score for feat, score in scores.items()}
    unkeywords = {feat: score for feat, score in
                  Counter(unscores).most_common(n_unkeywords)}
    return keywords, unkeywords
