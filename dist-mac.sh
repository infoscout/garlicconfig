#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/cget/lib

for i in $(ls /opt/python);
do
    /opt/python/$i/bin/python setup.py bdist_wheel;
done;

for i in $(ls dist);
do
    auditwheel repair dist/$i
done;
