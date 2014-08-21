#!/bin/bash

if [ -z "$WEB_CONCURRENCY" ]; then
    WEB_CONCURRENCY=3
fi

if [ -z "$PORT" ]; then
    PORT=5000
fi

gunicorn -b "0.0.0.0:$PORT" --workers $WEB_CONCURRENCY app:app
