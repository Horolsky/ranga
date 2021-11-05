#!/usr/bin/bash 

# draft testing script
# dirs ~/test and ~/pam_demo must exists before running this script

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REPO_DIR="$( dirname "$SCRIPT_DIR" )"
DEMO_DIR="$REPO_DIR/demo_assets"

APP_DATA="$HOME/.ffindex"
DATABASE="$APP_DATA/index.db"

FFINDEX="$REPO_DIR/ffindex"

# TESTLOG=$(mktemp /tmp/ffindex-test.log)
# writing >&3
# exec 3>"$TESTLOG"
# reading <&4
# exec 4<"$TESTLOG"

if [ ! -d "$DEMO_DIR" ]; then
    read -p "No demo files found, download media to $DEMO_DIR [Y/n]? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "Downloading..."
        $SCRIPT_DIR/get_media.sh
    else
        exit 0
    fi
fi
 
TEST_CASE_1() {
    # echo $($FFINDEX monitor -r)
    echo $($FFINDEX monitor --status )
}

TEST_CASE_2() {
    # echo "ffindex monitor -s"
    # echo "ffindex monitor --add $DEMO_DIR"
    $FFINDEX monitor --add $DEMO_DIR > /dev/null 2>&1
    LINES=$( $FFINDEX monitor --list | grep "$DEMO_DIR" -c )
    (( $LINES > 0)) && echo "PASSED" || echo "FAILED"
}

TEST_CASE_3() {
    LINES=$( $FFINDEX search -k "Deutsch" | wc -l )
    (($LINES > 0)) && echo "PASSED" || echo "FAILED"
}

TEST_CASE_4() {
    mkdir -p "$REPO_DIR/temp" 
    $FFINDEX monitor -a "$REPO_DIR/temp" > /dev/null 2>&1

    mkdir -p "$REPO_DIR/temp/deep/nested"
    touch "$REPO_DIR/temp/deep/nested/lol.txt"

    LINES1=$( $FFINDEX search -k lol | wc -l )

    rm -rf "$REPO_DIR/temp/deep"
    sleep 1
    LINES2=$( $FFINDEX search -k lol | grep lol -c )
    (($LINES1 > 0 && $LINES2 == 0)) && echo "PASSED" || echo "FAILED"
}

CLEANUP() {
    $FFINDEX monitor --stop
    rm $DATABASE > /dev/null 2>&1
}

echo "Running ffindex tests..."

CLEANUP
$FFINDEX monitor -r
for N in {1..4};
do
    echo
    echo "TEST CASE $N:"
    # PASSED=$(TEST_CASE_$N)
    echo $(TEST_CASE_$N)
    # (($PASSED)) && echo "PASSED" || echo "FAILED"
done
CLEANUP