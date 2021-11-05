#!/usr/bin/bash

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REPO_DIR="$( dirname "$SCRIPT_DIR" )"
DEMO_DIR="$REPO_DIR/demo_assets"

LINKS=$(<$SCRIPT_DIR/links.txt)
mkdir -p $DEMO_DIR

for l in ${LINKS[*]}
do
    wget -P $DEMO_DIR/ $l
done

echo "Demo media loaded into $DEMO_DIR"
