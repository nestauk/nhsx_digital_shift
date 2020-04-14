from newsapi import NewsApiClient
from newspaper import Article
from newspaper import ArticleException
from retrying import retry
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from gensim.models import Phrases
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import time

STOPWORDS = set(stopwords.words('english'))
PAGE_SIZE = 100
APIKEY = 'db3285bbe6844f268782e91f72c2b5c5'


@retry(wait_fixed=1000, stop_max_attempt_number=2)
def parse(url):
    article = Article(url)
    article.download()
    time.sleep(1)
    article.parse()
    article.nlp()
    return article


def articles(api_key, **kwargs):
    newsapi = NewsApiClient(api_key=api_key)
    results_so_far = 0
    total_results = None
    kwargs['page'] = 0
    while results_so_far != total_results:
        kwargs['page'] += 1
        results = newsapi.get_everything(**kwargs)
        if total_results is None:
            print(results['totalResults'])
        for article in results['articles']:
            try:
                parsed_article = parse(article['url'])
            except ArticleException:
                continue
            article['parsed_article'] = parsed_article
            yield article
        total_results = results['totalResults']
        results_so_far += len(results['articles'])


def tokenize(docs):
    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(docs)):
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]

    lemmatizer = WordNetLemmatizer()
    docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]

    # Add bigrams and trigrams to docs (only ones that appear 20 times or more).
    bigram = Phrases(docs, min_count=int(0.1*len(docs)))
    for idx in range(len(docs)):
        for token in bigram[docs[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)

    # Remove short tokens
    docs = [[token for token in doc if len(token) > 2] for doc in docs]

    # Remove stopwords
    docs = [[token for token in doc if token not in STOPWORDS] for doc in docs]
    return docs


def generate_topics(docs):
    docs = tokenize(docs)

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)

    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=20, no_above=0.9)
    # Bag-of-words representation of the documents.
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))

    # Set training parameters.
    num_topics = 10
    chunksize = 2000
    passes = 20
    iterations = 400
    eval_every = None  # Don't evaluate model perplexity, takes too much time

    # Make a index to word dictionary.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token
    model = LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=chunksize,
        alpha='auto',
        eta='auto',
        iterations=iterations,
        num_topics=num_topics,
        passes=passes,
        eval_every=eval_every
    )
    top_topics = model.top_topics(corpus)
    for topic, _ in top_topics:
        terms = []
        score = 0
        for _score, _term in topic:
            score += _score
            terms.append(_term)
            if score > 0.75:
                break
    return '__'.join(terms)


def expand_keywords(documents, search_terms):
    docs = [' '.join(tokens) for tokens in tokenize(documents)]

    vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=500,
                                 binary=True, stop_words='english')
    X = vectorizer.fit_transform(docs)
    Xc = (X.T * X)  # this is co-occurrence matrix in sparse csr format
    Xc.setdiag(0)  # sometimes you want to fill same word cooccurence to 0

    feature_names = vectorizer.get_feature_names()
    cooc = Xc.todense()
    stops = [x for x, _ in Counter({feature: sum(cooc[idx].tolist()[0])
             for idx, feature in enumerate(feature_names)}).most_common(10)]

    expanded_terms = []
    for term in search_terms:
        if term in feature_names:
            idx = feature_names.index(term)
            _cooc = {feature: count
                     for count, feature in
                     zip(cooc[idx].tolist()[0], feature_names)}
            cooc_terms = []
            for x, _ in Counter(_cooc).most_common():
                if x in stops:
                    continue
                cooc_terms.append(x)
                if len(cooc_terms) == 10:
                    break
            expanded_terms.append(cooc_terms)
    return expanded_terms


if __name__ == '__main__':
    query = '(NHS OR "National Health Service") AND -football'
    all_articles = []
    for article in articles(api_key=APIKEY,
                            q=query, from_param='2020-03-14',
                            language='en', sort_by='publishedAt',
                            page_size=100):
        all_articles.append(article)
        if len(all_articles) == 100:
            break

    documents = [article['parsed_article'].summary for article in all_articles]
    keywords = expand_keywords(documents, ['app', 'telemedicine', 'remote', 'consultation',
                                           'gp', 'digital', 'online'])
    # expand search, identify topics, then predict articles
    topics = generate_topics(documents)
    
