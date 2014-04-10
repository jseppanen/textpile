#!/bin/sh
cd /srv/textpile
. bin/activate
yesterday=$(date --date="yesterday" +%Y-%m-%d)
bin/python crawl.py data $yesterday >logs/crawl.$yesterday.log 2>&1
bin/python load_db.py data/*.$yesterday.msgpack
bin/python update_relevance.py
