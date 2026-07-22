#!/usr/bin/env bash

TAG=$(git describe --tags --exact-match 2>/dev/null)

if [ -n "$TAG" ]; then
  VERSION="$TAG"
else
  # Fallback for untagged commits: short SHA (or GITHUB_SHA)
  VERSION=$(git rev-parse --short HEAD)
fi

# # if the latest (HEAD) commit is tagless (in vX.X.X format), the workflow shuts down gracefully
# if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]];
# then
#   echo "No suitable tag found, skipping build"
#   echo "built=false" >> $GITHUB_OUTPUT
#   exit 0 
# fi

echo "$VERSION" > src/version.txt

docker image build -t hivebox:$VERSION .
echo "built=true" >> $GITHUB_OUTPUT
echo "image_version=$VERSION" >> $GITHUB_OUTPUT