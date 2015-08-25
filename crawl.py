# -*- encoding: utf-8 -*-

import sys
import requests
import datetime as dt
import time
import msgpack
import re
import logging
from collections import defaultdict
from itertools import groupby

execfile('config/crawl.conf.py')

# crawl.py <data-dir> [date]

logging.basicConfig(level=logging.INFO)

datadir = sys.argv[1]
if len(sys.argv) == 3:
    query_date = sys.argv[2]
else:
    query_date = None

def ratelimiter(hz):
    t=[0]
    p=1.0/hz
    def ratelimit():
        d=p-(time.time()-t[0])
        if (d>0):
            time.sleep(d)
        t[0]=time.time()
    return ratelimit

def search(params, ratelimit):
    params=params.copy()
    while 1:
        ratelimit()
        t=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
        r=requests.get(search_url, params=params, headers=headers)
        logging.info('got %d %s', r.status_code, r.url)
        meta={
            'request_time': t,
            'url': r.url,
            'status_code': r.status_code,
            'elapsed': r.elapsed.total_seconds(),
            'headers': dict(r.headers)
        }
        res=r.json()
        for j in res['jobs']:
            j['_search_meta'] = meta.copy()
            yield j
        if 'time' not in params:
            params['time'] = res['timestamp']
        if 'offset' not in params:
            params['offset'] = 0
        params['offset'] += res['numReturned']
        if params['offset'] >= res['numFound']:
            return

date_re = re.compile(r'^(\d\d?)\.(\d\d?)\.(\d\d\d\d)$')

def crawl(params, query_date):
    params['sort_by'] = 'publication_time'
    params['sort_order'] = 'DESC'
    ratelimit=ratelimiter(2)
    for doc in search(params, ratelimit):
        m = date_re.search(doc['publication_time'])
        if m is None:
            logging.warning('parse error: publication_time: %s', doc['publication_time'])
            continue
        day, month, year = map(int, m.groups())
        date = '%04d-%02d-%02d' % (year, month, day)
        if query_date:
            if date > query_date:
                continue
            elif date < query_date:
                return
        ratelimit()
        t=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
        r = requests.get(doc['job_url'], headers=headers)
        logging.info('got %d %s', r.status_code, r.url)
        doc['_page_meta'] = {
            'request_time': t,
            'url': r.url,
            'status_code': r.status_code,
            'elapsed': r.elapsed.total_seconds(),
            'headers': dict(r.headers),
            'encoding': r.encoding
        }
        doc['_page'] = r.text
        yield date, doc

res=crawl(search_params, query_date)
for date, group in groupby(res, lambda x: x[0]):
    docs = [d for x,d in group]
    with file(datadir + '/%s.%s.msgpack' % (host, date), 'w') as f:
        msgpack.pack(docs, f)
