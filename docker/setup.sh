#!/bin/sh
for i in $(ls /opt/python);
do
    /opt/python/$i/bin/pip install cython;
done;
