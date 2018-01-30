if git diff HEAD~ --name-only|grep $1 &>/dev/null; then
    # Folder is in latest check in
    exit 0
else
    exit 1
fi;
