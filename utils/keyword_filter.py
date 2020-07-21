"""
keyword_filter
==============

Filter, rank and save NewsAPI articles based on lists of keywords
"""

from utils.datapath import datapath
from utils.news_api import NEWSAPI_DATEFORMAT, NEWSAPI_TIMEFORMAT
from datetime import datetime
import pandas as pd
import json
import inflect
from collections import Counter

INFLECT = inflect.engine()


def _expand_terms(first_terms, second_terms=[]):
    """Expand pairs of sets of terms.

    Firstly, :obj:`second_terms` is expanded to include plural forms.
    Then, all combinations of :obj:`first_terms` and :obj:`second_terms`
    are generated.

    e.g. ['video'], ['chat', 'call'] --> ['video chat', 'video chats',
                                          'video call', 'video calls']

    If :obj:`second_terms` is missing then it is ignored.

    e.g. ['triage online'] --> 'triage online'

    Args:
        first_terms (list): List of first terms
        second_terms (list): List of second terms, which will also be pluralised.
    Returns:
        expanded_terms (list): Flat list of expanded terms.
    """
    queries = [] if second_terms != [] else first_terms
    for first_term in first_terms:
        for second_term in second_terms:
            queries.append(f'{first_term} {second_term}')
            queries.append(f'{first_term} {INFLECT.plural(second_term)}')
    return queries


def expand_terms(seed_terms):
    '''Expand all seed terms, each in the format described in
       :obj:`_expand_terms`.

    Args:
        seed_terms (list): List of :obj:`first_terms` and :obj:`second_terms`,
                           as described in :obj:`_expand_terms`.
    Returns:
        expanded_terms (list): Flat list of expanded terms.
    '''
    queries = []
    for terms in seed_terms:
        queries += _expand_terms(*terms)
    return queries


def filter_articles(articles, core_terms, seed_terms,
                    min_core_df=5, min_seed_df=None):
    '''Filter articles by requiring minimum content of core (those used query
    hit NewsAPI) and seed terms (contextual keywords). Results are returned
    with a ranking score = (sum_core_terms * sum_seed_terms)/len(text).

    Args:
        articles (list): list of dict (each article is the rawish
                         response from NewsAPI)
        core_terms (list): Terms used to query the NewsAPI
        seed_terms (list): Context terms to further refine the articles.
        min_core_df (int): Minimum sum of occurences of core terms per article.
        min_seed_df (int): Minimum sum of occurences of seed terms per article.
                           If :obj:`None`, defaults to :obj:`min_core_df`.
    Returns:
       articles (dict): Filtered set of articles, with associated rank.
    '''
    if min_seed_df is None:
        min_seed_df = min_core_df
    expanded_seed_terms = expand_terms(seed_terms)
    ranked_articles = {}
    titles = set()  # Keep track of articles to avoid counting duplicates
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


def save_excel(ranked_articles, label):
    '''Save the ranked articles in a nicely formatted Excel file'''
    output = []
    titles = set()
    for idx, rank in Counter(ranked_articles).most_common():
        art = articles[idx]
        if art['title'] in titles:
            continue
        titles.add(art['title'])
        source = art.pop('source')['name']
        publishedAt = datetime.strptime(art.pop('publishedAt'),
                                        NEWSAPI_DATEFORMAT+NEWSAPI_TIMEFORMAT)
        publishedAt = datetime.strftime(publishedAt, '%d/%m/%Y')
        output.append(dict(score=rank, source=source,
                           publishedAt=publishedAt, **art))
    df = pd.DataFrame(output, columns=['publishedAt', 'score', 'source', 'title',
                                       'author', 'description', 'content', 'url'])
    filename = datapath('outputs', f'{label}.xlsx')
    df.to_excel(filename)


if __name__ == '__main__':
    from utils.news_api import download_articles

    # An OR of all of these terms is used for the API query
    core_terms = [['nhs', 'national health service']]

    # Format: Pairs of lists of form (A=[a0,..,an], B=[b0,...,bn])
    # Firstly, B is expanded to include plural forms
    # Then, all combinations of A and B are generated
    # e.g. ['video'], ['chat', 'call'] --> ['video chat', 'video chats',
    #                                       'video call', 'video calls']
    # If B is missing then it is ignored
    # e.g. ['triage online'] --> 'triage online'
    #
    # These terms are then searched for AFTER the API query for filtering articles
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

    # Core arguments for all API calls
    initial_kwargs = dict(page_size=100,
                          language='en',
                          q=' OR '.join(f'("{term}")' for term in core_terms[0]),
                          sort_by='publishedAt', verbose=True)

    # Collect and save from June 2019 til present
    label = 'nhs_since_june2019'
    articles = download_articles(label, start='01 June, 2019',
                                 **initial_kwargs)
    ranked_articles = filter_articles(articles, core_terms, seed_terms,
                                      min_core_df=4, min_seed_df=2) # Less tight requirements
    filename = datapath('processed', f'filtered_{label}.json')
    with open(filename, 'w') as f:
        f.write(json.dumps(ranked_articles))

    # Collect and save from March 2020 til present
    label = 'nhs_since_march_2'
    articles = download_articles('nhs_since_march_2', **initial_kwargs)
    ranked_articles = filter_articles(articles, core_terms, seed_terms) # Default tight requirements
    filename = datapath('processed', f'filtered_{label}.json')
    with open(filename, 'w') as f:
        f.write(json.dumps(ranked_articles))
    save_excel(ranked_articles, 'nhsx_digital_shift_news_v2')
