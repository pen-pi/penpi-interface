#! /bin/sh
DIR=$(dirname $0)
PYTHON=${PYTHON:-python3}
PYTHONPATH=$DIR exec $PYTHON -m penpi $@
