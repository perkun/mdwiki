#!/bin/bash
# created by perkun on 22/07/2021

sudo rm -r ~/.cache/Python-Eggs/mdwiki*

cd css
make
cd ..
sudo python setup.py install --force
