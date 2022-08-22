#!/bin/sh

CURRENT_DIR=$(pwd)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CURRENT_DIR/cget/lib:$CURRENT_DIR/cget/lib64

rm -fr build
rm -fr dist


repair_dist () {
    for i in $(ls dist);
    do
        auditwheel repair --plat manylinux_2_31_x86_64 dist/$i
    done;
    rm -fr build
    rm -fr dist
}


pip install auditwheel
python setup.py bdist_wheel
repair_dist
