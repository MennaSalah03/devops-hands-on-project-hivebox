#! /bin/env bash

VERSION=$(git tag -l --sort=-taggerdate | grep v[0-9].[0-9].[0-9] | head -1)

# if the latest (HEAD) commit is tagless (in vX.X.X format), the workflow shuts down gracefully
if [ -z "$VERSION" ]; then
  echo "No tag found, skipping build"
  echo "built=false" >> $GITHUB_OUTPUT
  exit 0 
fi
echo "$VERSION" > src/version.txt

docker image build -t hivebox:${VERSION:1} -t hivebox:latest .
echo "built=true" >> $GITHUB_OUTPUT