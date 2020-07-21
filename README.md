# nhsx_digital_shift

Pilot studies for NHSx on understanding the digital shift and trends in End Of Life care due to the lockdown during the COVID-19 pandemic.

a) Automated filtering of news articles discussing remote and digital services, relating to the NHS

b) An analysis of Google Play Store reviews relating to GP (and similar) service apps

c) Automated filtering of news articles discussing End Of Life (EOL) care in the UK.

More information on studies a) and b) can be found in the [following slide deck](https://docs.google.com/presentation/d/1u24Tr792cP01YHJoEgEJ1EdNNPKSD6Q2Xh7QK50KpEA/edit?usp=sharing) (Nesta staff only)
In general, refer to these slides for methodological notes.


## a) Filtering of news articles (remote and digital services in the UK)
### i) Collecting news articles

We use the NewsAPI API (note: this isn't free) to collect relevant news articles. 
Please see `__name__ == '__main__'` in `utils.keyword_filter` for how to do this.
News articles are collected according to various querying strategies, as discussed in the methodological slide deck.

### ii) [Data-driven filtering and ranking](https://github.com/nestauk/nhsx_digital_shift/blob/master/notebooks/digital_services/news_filter_data_driven.ipynb)
### iii) [Keyword-driven filtering and ranking](https://github.com/nestauk/nhsx_digital_shift/blob/master/utils/keyword_filter.py#L127)

#### Notes for NHS team running this

The following instructions assume a UNIX-like system (e.g. this works on both my MacBook and cloud Linux server). On Windows I would first recommend using the Windows-Linux Subsystem, and then using the Ubuntu interface on there.

Firstly, [install conda on your local machine](https://docs.conda.io/projects/conda/en/latest/user-guide/install/). 

After this you can create an environment to work in:

```
conda create -y -n nhsx python=3.7 pandas
conda activate nhsx
pip install inflect
pip install newsapi-python
pip install openpyxl
```

Next, get the code from this repository:

```
git clone https://github.com/nestauk/nhsx_digital_shift
cd nhsx_digital_shift
mkdir secrets
export PYTHONPATH=$PWD
```

Now you will need a NewsAPI key. You should store this in a file called `news_api_key` and the contents of the file should be the key only. Now you should copy the file `news_api_key` which you created into the folder `secrets`, e.g.:

```
cp /path/to/news_api_key secrets
```

Finally, you can run the data collection and processing code:

```
python utils/keyword_filter.py
```

The output files will appear in your current working directory.

## b) Health app reviews
### i) [Collecting playstore reviews](https://github.com/nestauk/nhsx_playscrape/blob/master/playscrape/playscrape.py)
### ii) [Exploratory and sentiment analysis](https://github.com/nestauk/nhsx_digital_shift/blob/master/notebooks/digital_services/health_app_reviews.ipynb)

## c) [Filtering of news articles (End of Life care in the UK)](https://github.com/nestauk/nhsx_digital_shift/blob/master/notebooks/eol_care/collect_eol_news.ipynb)