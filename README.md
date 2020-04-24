# nhsx_digital_shift

Pilot studies for NHSx on understanding the digital shift due to the lockdown during the COVID-19 pandemic.

a) Automated filtering of news articles discussing remote and digital services, relating to the NHS

b) An analysis of Google Play Store reviews relating to GP (and similar) service apps

More information can be found in the [following slide deck](https://docs.google.com/presentation/d/1u24Tr792cP01YHJoEgEJ1EdNNPKSD6Q2Xh7QK50KpEA/edit?usp=sharing) (Nesta staff only)
In general, refer to these slides for methodological notes.

## a) Filtering of news articles
### i) Collecting news articles

We use the NewsAPI API (note: this isn't free) to collect relevant news articles. 
Please see `__name__ == '__main__'` in `utils.keyword_filter` for how to do this.
News articles are collected according to various querying strategies, as discussed in the methodological slide deck.

### ii) [Data-driven filtering and ranking](https://github.com/nestauk/nhsx_digital_shift/blob/master/notebooks/news_filter_data_driven.ipynb)
### iii) [Keyword-driven filtering and ranking](https://github.com/nestauk/nhsx_digital_shift/blob/master/utils/keyword_filter.py#L127)

## b) Health app reviews
### i) [Collecting playstore reviews](https://github.com/nestauk/nhsx_playscrape/blob/master/playscrape/playscrape.py)
### ii) [Exploratory and sentiment analysis](https://github.com/nestauk/nhsx_digital_shift/blob/master/notebooks/health_app_reviews.ipynb)