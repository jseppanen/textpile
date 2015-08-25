#!/bin/sh
cd /srv/textpile
yesterday=$(date --date="yesterday" +%Y-%m-%d)
mkdir -p data/crawl logs/crawl
python crawl.py data/crawl $yesterday >logs/crawl/crawl.$yesterday.log 2>&1
python load_db.py data/crawl/*.$yesterday.msgpack
python update_relevance.py
