#! /bin/bash

echo "heizung will be installed in this directory:"
pwd
echo "succeed?"
read

echo "Creating venv..."
python3 -m venv venv

echo "Entering venv..."
source venv/bin/activate

echo "Installing requirements..."
pip3 install -r requirements.txt

echo "Setting up environment..."
export PYTHONPATH=./
python3 system/setup.py
