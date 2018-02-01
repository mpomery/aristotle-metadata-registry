export MODULE=$1
export TOX_ENV_TO_RUN=$2

if ./scripts/check_path.sh python/$MODULE || ./scripts/check_path.sh python/aristotle-metadata-registry; then
  cd $TRAVIS_BUILD_DIR/python/$MODULE
  tox -e $TOX_ENV_TO_RUN --skip-missing-interpreters
  export OUT_CODE=$?
  cd -
fi;
exit $OUT_CODE