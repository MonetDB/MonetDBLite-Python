#!/bin/bash

set -e -x

#yum install pandoc

# pyver_list=(cp27-cp27m cp27-cp27mu cp34-cp34m cp35-cp35m cp36-cp36m cp37-cp37m)
# pyver_list=(cp27-cp27mu cp34-cp34m cp35-cp35m cp36-cp36m cp37-cp37m)
pyver_list=(cp37-cp37m)

pushd /io/

# Compile wheels
for ptn in "${pyver_list[@]}"; do
    PYBIN="/opt/python/${ptn}/bin"
    "${PYBIN}/pip" install -r /io/dev-requirements.txt
    "${PYBIN}/python" setup.py bdist_wheel
done

# Bundle external shared libraries into the wheels
pushd /io/dist/
for whl in *monetdblite*-linux_*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
    rm "$whl"
done

popd
pushd /io/wheelhouse/

for whl in *monetdblite*-manylinux1_*.whl; do
    cp "$whl" /io/dist/
done

popd

# Install packages and test
for ptn in "${pyver_list[@]}"; do
    PYBIN="/opt/python/${ptn}/bin"
    "${PYBIN}/pip" install monetdblite --no-index -f /io/dist
    # Prepare and upload a coverage report when using the latest
    # python
    if [ "${ptn}" == "cp37-cp37m" ]; then
	"${PYBIN}/coverage" run --source=/io/lib/monetdblite setup.py test
	# "${PYBIN}/coveralls"
    else
	"${PYBIN}/python" setup.py test
    fi
done

# Cleanup
rm -rf build/ wheelhouse/
