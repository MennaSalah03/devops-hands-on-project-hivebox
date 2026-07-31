#!/usr/bin/env bash

VERSION=$(git rev-parse --short HEAD)
echo "$VERSION" > src/version.txt

docker image build -t hivebox:$VERSION .
echo "built=true" >> $GITHUB_OUTPUT
echo "image_version=$VERSION" >> $GITHUB_OUTPUT