#!/bin/bash

# Inicia Streamlit en segundo plano
streamlit run app.py &

# Inicia Uvicorn en el puerto 8010
uvicorn chromadb.app:app --host 0.0.0.0 --port 8010
