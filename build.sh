#! /bin/env bash

VERSION_FILE=src/version.txt

git tag -l --sort=-taggerdate | grep v[0-9].[0-9].[0-9] | head -1 > $VERSION_FILE

VERSION=$(cat $VERSION_FILE)

docker image build -t hivebox:${VERSION:1} -t hivebox:latest .
