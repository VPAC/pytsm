#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

RETURN=0
cd $DIR

echo ""
echo "FLAKE8"
echo "############################"
flake8 .
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

echo ""
echo "TESTS - Python 2"
echo "############################"
python2 setup.py test
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

echo ""
echo "TESTS - Python 3"
echo "############################"
python3 setup.py test
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

exit $RETURN
