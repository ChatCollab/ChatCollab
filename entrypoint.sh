#!/bin/sh

uvicorn chatcollab.timeline.main:app & streamlit run "/chatcollab/main.py"