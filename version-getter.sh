#! /bin/env bash

VERSION_FILE=src/version.txt

git tag | tail -1 > $VERSION_FILE
