#!/bin/bash
# created by perkun on 22/07/2021

cd css
make
cd ..
sudo python setup.py install --force
