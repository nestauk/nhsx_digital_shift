from newsapi import NewsApiClient
from dateutil import rrule
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import inflect
from collections import Counter

INFLECT = inflect.engine()
NEWSAPI_DATEFORMAT='%Y-%m-%d'
NEWSAPI_TIMEFORMAT='T%H:%M:%SZ'


def get_articles(api_key, verbose=False, **kwargs):
    results_so_far = 0
    total_results = None
    kwargs['page'] = 1
    while results_so_far != total_results and kwargs['page'] < 100:
        newsapi = NewsApiClient(api_key=api_key)
        results = newsapi.get_everything(**kwargs)
        if total_results is None and verbose:
            print(f"{results['totalResults']} results found for {kwargs}")
        for article in results['articles']:
            yield article
        total_results = results['totalResults']
        results_so_far += len(results['articles'])
        kwargs['page'] += 1


def _expand_terms(first_terms, second_terms=[]):
    queries = [] if second_terms != [] else first_terms
    for first_term in first_terms:
        for second_term in second_terms:
            queries.append(f'{first_term} {second_term}')
            queries.append(f'{first_term} {INFLECT.plural(second_term)}')
    return queries


def expand_terms(seed_terms):
    queries = []
    for terms in seed_terms:
        queries += _expand_terms(*terms)
    return queries


def filter_articles(articles, core_terms, seed_terms,
                    min_core_df=5, min_seed_df=None):
    if min_seed_df is None:
        min_seed_df = min_core_df
    expanded_seed_terms = expand_terms(seed_terms)
    ranked_articles = {}
    titles = set()
    for i, article in enumerate(articles):
        if article['title'] in titles:
            continue
        titles.add(article['title'])
        if article['content'] is None and article['description'] is None:
            continue
        elif article['content'] is None:
            _content = article['description'].lower()
        else:
            _content = article['content'].lower()

        n_core = sum(_content.count(term) for term in core_terms[0])
        if n_core < min_core_df:
            continue
        n_seed = sum(_content.count(term) for term in expanded_seed_terms)
        if n_seed < min_seed_df:
            continue
        ranked_articles[i] = n_seed*n_core/len(_content)
    return ranked_articles


def weekchunks(start, until=None):
    if until is None:
        until = datetime.now()
    start = pd.Timestamp(start).to_pydatetime()
    chunks = [datetime.strftime(_date, NEWSAPI_DATEFORMAT)
              for _date in rrule.rrule(rrule.WEEKLY, dtstart=start,
                                       until=until)]
    chunk_pairs = []
    for i in range(len(chunks)-1):
        chunk_pairs.append((chunks[i], chunks[i+1]))
    return chunk_pairs


def download_articles(label, start='March 01, 2020',
                      until=None, **initial_kwargs):
    filename = f'{label}.json'
    titles = set()
    if not os.path.isfile(filename):
        articles = []
        for from_param, to in weekchunks(start, until):
            kwargs = dict(from_param=from_param, to=to, **initial_kwargs)
            for art in get_articles(**kwargs):
                if art['title'] in titles:
                    continue
                titles.add(art['title'])
                articles.append(art)
        with open(filename, 'w') as f:
            f.write(json.dumps(articles))
    else:
        with open(filename) as f:
            articles = json.load(f)
    return articles


if __name__ == '__main__':
    core_terms = [['nhs', 'national health service']]
    seed_terms = [[['digital'], ['transformation']],
                  [['digital health']],                 
                  [['health tech']],
                  [['digital'] + ['technology']],
                  [['video'], ['chat', 'call', 'consultation']],
                  [['remote'], ['consultation', 'diagnosis', 'monitoring']],
                  [['online', 'digital', 'phone'], ['consultation']],
                  [['telecare', 'telemedicine', 'telehealth']],
                  [['virtual medicine']],
                  [['triage online']],
                  [['online triage']],
                  [['triaging patients online']],
                  [['digital', 'virtual'], ['therapy', 'therapeutic']],
                  [['electronic', 'digital'], ['prescribing']],
                  [['patient data']],
                  [['data sharing']],
                  [['NHSX', 'NHS Digital']]]

    APIKEY = 'db3285bbe6844f268782e91f72c2b5c5'
    initial_kwargs = dict(api_key=APIKEY, page_size=100,
                          language='en',
                          q=' OR '.join(f'("{term}")' for term in core_terms[0]),
                          sort_by='publishedAt', verbose=True)
    label = 'nhs_since_june2019'
    articles = download_articles(label, start='01 June, 2019', **initial_kwargs)
    ranked_articles = filter_articles(articles, core_terms, seed_terms, min_core_df=4, min_seed_df=2)

    #articles = download_articles('nhs_since_march', **initial_kwargs)
    #ranked_articles = filter_articles(articles, core_terms, seed_terms)
    with open(f'filtered_{label}.json', 'w') as f:
        f.write(json.dumps(ranked_articles))

    # output = []
    # titles = set()
    # for idx, rank in Counter(ranked_articles).most_common():
    #     art = articles[idx]
    #     if art['title'] in titles:
    #         continue
    #     titles.add(art['title'])
    #     source = art.pop('source')['name']
    #     publishedAt = datetime.strptime(art.pop('publishedAt'),
    #                                     NEWSAPI_DATEFORMAT+NEWSAPI_TIMEFORMAT)
    #     publishedAt = datetime.strftime(publishedAt, '%d/%m/%Y')
    #     output.append(dict(score=rank, source=source,
    #                        publishedAt=publishedAt, **art))
    # df = pd.DataFrame(output, columns=['publishedAt', 'score', 'source', 'title',
    #                                    'author', 'description', 'content', 'url'])
    # df.to_excel('nhsx_digital_shift_news_v1.xlsx')
