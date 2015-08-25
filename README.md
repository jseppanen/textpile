# Textpile

Simple document classifyin' web app.

## Deployment

1. Build Docker image.

```
docker build -t textpile github.com/jseppanen/textpile
```

2. Create a container. Choose HTTP `<port>`.

```
docker create --restart=always -p <port>:80 --name textpile textpile
```

3. Configure Flask server and crawler. See `config/*.template`

```
docker cp flask-server.conf <container>:/srv/textpile/config/
docker cp crawl.conf.py <container>:/srv/textpile/config/
```

4. (optional) Import data. Find out where `/srv/textpile/data` volume
is mounted, and copy `textpile.db` there.

```
docker inspect <container>
```

5. Launch app.

```
docker start <container>
```

6. Configure host nginx (see config/nginx-proxy.conf)

## files

### web app

app, static, templates

### backend

server.py
config/server.conf(.template)

creation: init_db.py, schema.sql

### crawler and updater

config/crawl.conf.py(.template)
crawl.daily.cron
crawl.daily.sh
crawl.py
load_db.py
update_relevance.py

## Dependencies

See Dockerfile

## Copyright and license

Copyright © 2014, Jarno Seppänen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
