#!/bin/bash

set -e -x

#yum install pandoc

pyver_list=(cp27-cp27m cp34-cp34m cp35-cp35m cp36-cp36m cp37-cp37m)

pushd /io/

# Compile wheels
for ptn in "${pyver_list[@]}"; do
    PYBIN="/opt/python/${ptn}/bin"
    "${PYBIN}/pip" install -r /io/dev-requirements.txt
    "${PYBIN}/python" setup.py bdist_wheel
done

# Bundle external shared libraries into the wheels
for whl in dist/*monetdblite*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Install packages and test
for ptn in "${pyver_list[@]}"; do
    PYBIN="/opt/python/${ptn}/bin"
    "${PYBIN}/pip" install monetdblite_test --no-index -f /io/wheelhouse
    "${PYBIN}/python" -m pytest
done

# Cleanup
rm -rf build/ dist/

# Prepare for travis to upload
mv wheelhouse/ dist/
