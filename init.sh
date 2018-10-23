#!/bin/bash
PLATFORM=$(uname)

if [ $PLATFORM == 'Darwin' ]
then
    echo 'Detected Mac OS; Static Library Preferred!'
    cget init --std=c++11 --static
else
    echo 'Detected Linux; Shared Library Preferred!'
    cget init --std=c++11 --shared
fi

cget install --file=native_requirements.txt
