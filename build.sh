#! /bin/env bash

VERSION_FILE=src/version.txt

git tag -l --sort=-taggerdate | grep v[0-9].[0-9].[0-9] | head -1 > $VERSION_FILE

# if the latest (HEAD) commit is tagless (in vX.X.X format), the workflow shuts down gracefully
if [ -z "$VERSION" ]; then
  echo "No tag found, skipping build"
  exit 0 
fi

VERSION=$(cat $VERSION_FILE)

docker image build -t hivebox:${VERSION:1} -t hivebox:latest .
