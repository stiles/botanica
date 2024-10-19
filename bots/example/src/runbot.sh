#!/bin/bash
# Activate virtual environment, install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the main script
python3 main.py