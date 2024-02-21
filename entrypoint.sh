#!/bin/sh

uvicorn chatcollab.timeline.main:app && python3 chatcollab/run_slack_source.py && streamlit run "/chatcollab/main.py" --server.port 8080