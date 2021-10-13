#!/usr/bin/bash

DEMO_DIR=~/pam_demo
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

LINKS=$(<$SCRIPT_DIR/links.txt)
mkdir -p $DEMO_DIR

for l in ${LINKS[*]}
do
    wget -P $DEMO_DIR/ $l
done

echo "Demo media loaded into $DEMO_DIR"
