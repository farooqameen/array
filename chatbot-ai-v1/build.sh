#!/bin/bash

if [ "$1" == "dev" ]; then
  cp dockerfiles/.dockerignore.dev .dockerignore
  cp dockerfiles/Dockerfile.dev Dockerfile
  docker build -f Dockerfile -t prototype:dev .
elif [ "$1" == "prod" ]; then
  cp dockerfiles/.dockerignore.prod .dockerignore
  cp dockerfiles/Dockerfile.prod Dockerfile
  docker build -f Dockerfile -t prototype:prod .
elif [ "$1" == "local" ]; then
  cp dockerfiles/.dockerignore.local .dockerignore
  cp dockerfiles/Dockerfile.local Dockerfile
  cp dockerfiles/entrypoint_local.sh entrypoint_local.sh
  docker build -f Dockerfile -t prototype:local .
  rm entrypoint_local.sh
else
  echo "Usage: $0 {dev|prod|local}"
fi

# Restore original .dockerignore
mv .dockerignore dockerfiles/.dockerignore.backup
mv Dockerfile dockerfiles/Dockerfile.backup