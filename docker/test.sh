#!/usr/bin/env sh
PYTHON=/opt/python/${PYTHON_VERSION}/bin/python
PIP=/opt/python/${PYTHON_VERSION}/bin/pip
${PIP} uninstall garlicconfig -y
CGET_PATH=/cget ${PYTHON} /project/setup.py install --force
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cget/lib:/cget/lib64 ${PYTHON} /project/tests/tests.py
