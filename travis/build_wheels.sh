#!/bin/bash

set -e -x

#yum install pandoc

llst=(cp34-cp34m  cp35-cp35m  cp36-cp36m  cp37-cp37m)

# Compile wheels
for ptn in "${llst}"; do
    PYBIN="/opt/python/${ptn}/bin"
    "${PYBIN}/pip" install -r /io/dev-requirements.txt
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*monetdblite*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Install packages and test
for ptn in "${llst}"; do
    "${PYBIN}/pip" install monetdblite_test --no-index -f /io/wheelhouse
    (cd "$HOME"; "${PYBIN}/python" -m pytest)
done
