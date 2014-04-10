#!/bin/sh
. bin/activate
$PWD/bin/uwsgi --ini $PWD/config/uwsgi.ini &
disown -a
