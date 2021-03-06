import msgpack
from bs4 import BeautifulSoup, Tag, NavigableString
import re
import warnings

def load(paths):
    for path in sorted(paths):
        for doc in msgpack.unpack(file(path), encoding='utf-8'):
            soup=BeautifulSoup(doc['_page'])
            desc=soup.find(id='jobDescription').text
            try:
                date=parse_publication_time(doc['publication_time'])
            except ValueError, err:
                warnings.warn(str(err))
                continue
            yield dict(title=doc['name'], desc=desc,
                       url=doc['job_url'], company=doc['employer'],
                       location=doc['location_text'],
                       published=date)

def load_ilmo(path):
    soup=BeautifulSoup(file(path))
    title = None
    desc = []
    for el in soup.body.descendants:
        if el.name == 'h1' and el.text.strip():
            if title is not None:
                assert desc
                yield dict(title=title, desc=' '.join(desc))
            title = el.text.strip()
            desc = []
        elif isinstance(el, NavigableString):
            txt = unicode(el).strip()
            if txt:
                desc.append(txt)
    if title is not None:
        assert desc
        yield dict(title=title, desc=' '.join(desc))

date_re = re.compile(r'^(\d\d?)\.(\d\d?)\.(\d\d\d\d)$')
def parse_publication_time(txt):
    m = date_re.search(txt)
    if m is None:
        raise ValueError, 'parse error: %s', txt
    day, month, year = map(int, m.groups())
    return '%04d-%02d-%02d' % (year, month, day)
