
FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
        wget \
        ca-certificates \
        nginx

RUN wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh && \
    /bin/bash /Miniconda-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda-latest-Linux-x86_64.sh && \
    /opt/conda/bin/conda update -y conda
ENV PATH /opt/conda/bin:$PATH

RUN conda install -y \
        requests msgpack-python lxml html5lib \
        numpy scipy scikit-learn cython gensim \
        flask \
        supervisor

# more ugly deps
RUN conda install -y -c http://conda.anaconda.org/cgat beautifulsoup4
RUN conda install -y -c http://conda.anaconda.org/kalefranz uwsgi

RUN mkdir -p /srv/textpile /srv/textpile/data /srv/textpile/logs

WORKDIR /srv/textpile

ADD . /srv/textpile/

# create empty database
RUN python init_db.py

# configure
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /srv/textpile/config/nginx.conf /etc/nginx/sites-enabled/

RUN cp /srv/textpile/crawl.daily.cron /etc/crontab
RUN chmod 644 /etc/crontab

VOLUME /srv/textpile/data
VOLUME /srv/textpile/config
VOLUME /srv/textpile/logs

EXPOSE 80

# Launch nginx, uwsgi, and cron servers
CMD ["supervisord", "-c", "/srv/textpile/config/supervisord.conf"]
