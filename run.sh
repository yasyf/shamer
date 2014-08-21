#!/bin/bash

if [ -z "$WEB_CONCURRENCY" ]; then
    WEB_CONCURRENCY=3
fi

if [ -z "$PORT" ]; then
    PORT=5000
fi

if [ -n "$MONGOLAB_URI" ]; then
    MONGO_URI=$MONGOLAB_URI
fi

gunicorn -b "0.0.0.0:$PORT" --workers $WEB_CONCURRENCY app:app
