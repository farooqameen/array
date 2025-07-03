#!/bin/bash

if [ "$1" = 'server' ]; then
    exec python -m backend_server.app
elif [ "$1" = 'test' ]; then
    cd .. && pytest
elif [ "$1" = 'evaluate' ]; then
    exec python -m evaluation.test -c "$2"
else
    echo 'No command specified (server | test | evaluate {config/..config file...json})'
fi