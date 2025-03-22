#!/bin/sh
chown -R duser:duser /lapscraping
uvicorn main:app --reload --host 0.0.0.0 --port 8000
