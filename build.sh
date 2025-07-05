#!/usr/bin/env bash
pip install --no-build-isolation -r requirements.txt
python -m spacy download en_core_web_sm
