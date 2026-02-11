#!/usr/bin/env bash

# Start FastAPI in background on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit on Render PORT
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
