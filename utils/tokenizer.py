from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from gensim.models.phrases import Phrases

STOPHTML = ['nbsp', 'amp', 'gt', 'lt', 'quot', 'apos',
            'td', 'tr', 'li', 'ul', 'al']
STOPWORDS = set(list(stopwords.words('english') + STOPHTML))


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
