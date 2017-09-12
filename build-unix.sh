#!/bin/sh
cd src

# FIXME: hard-coded extension
rm -f build/libmonetdb5.so
make -j
mv build/libmonetdb5.so ..
cd ..
