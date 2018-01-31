if git diff --name-only HEAD...$TRAVIS_BRANCH|grep ^python/$1 &>/dev/null; then
    # Folder is in latest check in
    exit 0
else
    exit 1
fi;
