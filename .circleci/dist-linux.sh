#!/bin/sh

# CURRENT_DIR=$(pwd)
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CURRENT_DIR/cget/lib:$CURRENT_DIR/cget/lib64

rm -fr build
rm -fr dist


repair_dist () {
    for i in $(ls dist);
    do
        auditwheel repair dist/$i
    done;
    rm -fr build
    rm -fr dist
}


python setup.py bdist_wheel
repair_dist
