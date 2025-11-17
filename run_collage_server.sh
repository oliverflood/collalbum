#!/bin/bash
uvicorn collage_server.collage_api:app --host 0.0.0.0 --port 5000 --workers 4