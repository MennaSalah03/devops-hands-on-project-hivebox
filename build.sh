#! /bin/env bash

VERSION_FILE=src/version.txt

git tag | tail -1 > $VERSION_FILE

VERSION=$(cat src/version.txt)

docker image build -t hivebox:$VERSION -t hivebox:latest .
