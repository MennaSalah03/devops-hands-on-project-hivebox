#! /bin/env bash

./version-getter.sh

VERSION=$(cat src/version.txt)

docker image build -t hivebox:$VERSION -t hivebox:latest .
