'''
news_api
========

Collect data from NewsAPI in week chunks.
'''

from utils.secrets import news_api_key
from utils.datapath import datapath
from newsapi import NewsApiClient
from dateutil import rrule
from datetime import datetime, timedelta
from pandas import Timestamp
import os
import json

NEWSAPI_DATEFORMAT = '%Y-%m-%d'
NEWSAPI_TIMEFORMAT = 'T%H:%M:%SZ'


def get_articles(verbose=False, **kwargs):
    """Hit the NewsAPI via the get_everything method.
    Use this function as you would the NewsApiClient.get_everything method.

    Yields:
        One article at a time, buffered from NewsAPI.
    """
    results_so_far = 0
    total_results = None
    kwargs['page'] = 1
    while results_so_far != total_results and kwargs['page'] < 100:
        newsapi = NewsApiClient(api_key=news_api_key())  # NB: news_api_key is cached
        results = newsapi.get_everything(**kwargs)
        if total_results is None and verbose:
            print(f"{results['totalResults']} results found for {kwargs}")
        for article in results['articles']:
            yield article
        total_results = results['totalResults']
        results_so_far += len(results['articles'])
        kwargs['page'] += 1


def weekchunks(start, until=None):
    '''Generate date strings in weekly chunks between two dates.

    Args:
        start (str): Sensibly formatted datestring (format to be guessed by pd)
        until (str): Another datestring. Default=today.
    Returns:
        chunk_pairs (list): List of pairs of string, representing the start and end of weeks.
    '''
    if until is None:
        until = datetime.now()
    start = Timestamp(start).to_pydatetime()
    chunks = [datetime.strftime(_date, NEWSAPI_DATEFORMAT)
              for _date in rrule.rrule(rrule.WEEKLY, dtstart=start,
                                       until=until)]
    chunk_pairs = []
    for i in range(len(chunks)-1):
        chunk_pairs.append((chunks[i], chunks[i+1]))
    return chunk_pairs


def download_articles(label, start='March 01, 2020',
                      until=None, **initial_kwargs):
    '''Download articles from NewsAPI and save to json, between two dates. 
    If already downloaded, just load up the articles.

    Args:
        label (str): Label used to save the JSON output (don't include the .json)
        start (str): Sensibly formatted datestring (format to be guessed by pd)
        until (str): Another datestring. Default=today.
        news_api_kwargs (**kwargs): All other kwargs to pass to NewsApiClient.get_everything (e.g. the query)    
    Returns:
        articles
    '''
    filename = datapath('raw', f'{label}.json')
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
