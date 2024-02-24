#!/bin/sh

uvicorn chatcollab.timeline.main:app --host 0.0.0.0 --port 8000 & python chatcollab/run_slack_source.py & streamlit run "/chatcollab/main.py" --server.port 8080 &

wait