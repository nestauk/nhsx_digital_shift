# News
from newsapi import NewsApiClient
from newspaper import Article
from newspaper import ArticleException
from retrying import retry

# NLP
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from gensim.models.phrases import Phrases
from sklearn.feature_extraction.text import CountVectorizer
import spacy

# Core
from collections import Counter
import time
import numpy as np
import json
import os

# Globals
NLP = spacy.load('en')
STOPWORDS = set(list(stopwords.words('english'))+['nbsp', 'amp', 'gt', 'lt', 'quot', 'apos',
                                                  'td', 'tr', 'li', 'ul', 'al'])
APIKEY = 'db3285bbe6844f268782e91f72c2b5c5'


def grammer(docs, size, min_frac=0.1, min_count=100, igram=2):
    frac_count = int(min_frac*len(docs))
    min_count = min_count if min_count < frac_count else frac_count
    if min_count < 2:
        min_count = 2
    bigram = Phrases(docs, min_count=min_count)
    for idx in range(len(docs)):
        for token in bigram[docs[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)
    if size > igram:
        return grammer(docs=docs, size=size, min_frac=min_frac,
                       min_count=min_count, igram=igram+1)
    return docs


def tokenize(articles, field):
    _docs = []
    for article in articles:
        for _field in [field, 'content', 'description', 'title']:
            text = article[_field]
            if text is not None:
                break
        if text is None:
            text = ''
        _docs.append(text)

    # Lemmatize
    docs = [' '.join(token.lemma_ if token.lemma_ != '-PRON-'
                     else str(token) for token in NLP(doc)) for doc in _docs]

    # Remove non-alphanums
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(docs)):
        docs[idx] = docs[idx].lower()  # Convert to lowercase
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words

    # Remove numbers
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]

    # # Add bigrams and trigrams to docs
    # docs = grammer(docs, size=3)

    # Remove short tokens
    docs = [[token for token in doc if len(token) > 1] for doc in docs]

    # Remove stopwords
    docs = [[token for token in doc
             if not all(t in STOPWORDS for t in token.split('_'))]
            for doc in docs]
    return docs


def matrix_fraction(X):
    _sum = X.sum(axis=0)
    return _sum/(_sum.sum())


def jlh(foreground, background):
    a = matrix_fraction(foreground)
    b = matrix_fraction(background)
    jlh_scores = np.asarray(a / b) * np.asarray(a - b)
    return list(jlh_scores[0])


def generate_keywords(docs, search_terms, max_df=0.95,
                      min_df=2, max_features=500, binary=False, threshold=0.3):
    search_terms = search_terms.split()
    # Scan the documents for the search term, and prepare the docs for analysis
    search_docs = [idx for idx, doc in enumerate(docs)
                   if all(term in doc for term in search_terms)]
    docs = [' '.join(doc) for doc in docs]
    search_docs = [docs[idx] for idx in search_docs]

    # Create count vectors of the foreground and background
    vectorizer = CountVectorizer(max_df=max_df, min_df=min_df,
                                 max_features=max_features,
                                 binary=binary, stop_words='english')
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
    unkeywords = {feat: score for feat, score in Counter(unscores).most_common(10)}
    return keywords, unkeywords



@retry(wait_fixed=1000, stop_max_attempt_number=2)
def parse(url):
    article = Article(url)
    article.download()
    time.sleep(1)
    article.parse()
    article.nlp()
    return article


def get_articles(api_key, **kwargs):
    results_so_far = 0
    total_results = None
    kwargs['page'] = 1
    while results_so_far != total_results and kwargs['page'] < 100:
        newsapi = NewsApiClient(api_key=api_key)
        results = newsapi.get_everything(**kwargs)
        if total_results is None:
            print(results['totalResults'])
        for article in results['articles']:
            yield article
        total_results = results['totalResults']
        results_so_far += len(results['articles'])
        kwargs['page'] += 1


def make_query(query, filename, limit, **kwargs):
    if not os.path.isfile(filename):
        articles = []
        for article in get_articles(q=query, **kwargs):
            articles.append(article)
            if len(articles) == limit:
                break
        with open(filename, 'w') as f:
            f.write(json.dumps(articles))
    else:
        with open(filename) as f:
            articles = json.load(f)
    return articles


if __name__ == '__main__':
    # Training:   June 2018 - June 2019
    # Testing:    July 2019 - Dec 2019
    # Validation: Jan 2020
    # Extrapolation: Feb 2020 - present

    # Iterate on the following:
    # # Train --> expand keywords
    # # Train --> New search with combined keywords minus unkeywords
    # # Train --> Can you find relevant documents?
    # # If yes:
    # # Testing --> Can you find relevant documents?
    # If yes:
    # Validation --> Can you find relevant documents?
    # If yes:
    # Extrapolation --> Can you find relevant documents?

    # Search for 10000 most relevant articles to
    # a) NHS / GP
    # b) Telemedicine "online appointment" "remote consulation"
    # c) Babylon health
    # => and expand related vocab
    # Now perform expansive query on articles to find most relevant

    initial_kwargs = dict(api_key=APIKEY, page_size=100,
                          language='en',
                          from_param='2018-06-01',
                          to='2019-06-01',
                          sort_by='relevancy')
    limit = 10000
    nhs_query = ('"nhs" OR (("national health service" AND '
                 '("uk" OR "british" OR "britain" OR "united kingdom")))')
    nhs_articles = make_query(nhs_query, 'health_articles.json', limit, **initial_kwargs)
    tech_articles = make_query('telemedicine', 'tech_articles.json', limit, **initial_kwargs)

    nhs_docs = tokenize(nhs_articles)
    tech_docs = tokenize(tech_articles)
    health_expansion_terms = ['gp', 'doctor', 'nhs', 'digital', 'babylon']
    health_expansion_terms = ['babylon', 'gp', 'telemedicine']
