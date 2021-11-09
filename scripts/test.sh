#!/usr/bin/bash 

# draft testing script
# dirs ~/test and ~/pam_demo must exists before running this script

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REPO_DIR="$( dirname "$SCRIPT_DIR" )"
DEMO_DIR="$REPO_DIR/demo_assets"

APP_DATA="$HOME/.ranga"
DATABASE="$APP_DATA/index.db"

RANGA="$REPO_DIR/ranga"

# TESTLOG=$(mktemp /tmp/ranga-test.log)
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
    # echo $($RANGA monitor -r)
    echo $($RANGA monitor --status )
}

TEST_CASE_2() {
    # echo "ranga monitor -s"
    # echo "ranga monitor --add $DEMO_DIR"
    $RANGA monitor --add $DEMO_DIR > /dev/null 2>&1
    LINES=$( $RANGA monitor --list | grep "$DEMO_DIR" -c )
    (( $LINES > 0)) && echo "PASSED" || echo "FAILED"
}

TEST_CASE_3() {
    LINES=$( $RANGA search -k "Deutsch" | wc -l )
    (($LINES > 0)) && echo "PASSED" || echo "FAILED"
}

TEST_CASE_4() {
    mkdir -p "$REPO_DIR/temp" 
    $RANGA monitor -a "$REPO_DIR/temp" > /dev/null 2>&1

    mkdir -p "$REPO_DIR/temp/deep/nested"
    touch "$REPO_DIR/temp/deep/nested/lol.txt"

    LINES1=$( $RANGA search -k lol | wc -l )

    rm -rf "$REPO_DIR/temp/deep"
    sleep 1
    LINES2=$( $RANGA search -k lol | grep lol -c )
    (($LINES1 > 0 && $LINES2 == 0)) && echo "PASSED" || echo "FAILED"
}

CLEANUP() {
    $RANGA monitor --stop
    rm $DATABASE > /dev/null 2>&1
}

echo "Running ranga tests..."

CLEANUP
$RANGA monitor -r
for N in {1..4};
do
    echo
    echo "TEST CASE $N:"
    # PASSED=$(TEST_CASE_$N)
    echo $(TEST_CASE_$N)
    # (($PASSED)) && echo "PASSED" || echo "FAILED"
done
CLEANUP