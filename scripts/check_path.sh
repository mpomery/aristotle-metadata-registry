if git diff --name-only $TRAVIS_BRANCH...HEAD|grep ^$1 &>/dev/null; then
    # Folder is in latest check in
    exit 0
else
    echo "No changes to" $1 "on branch" $TRAVIS_BRANCH "skipping tests"
    exit 1
fi;
