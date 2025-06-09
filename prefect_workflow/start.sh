#!/bin/bash
echo "Setting up Prefect configuration..."

prefect config set PREFECT_API_URL="${PREFECT_API_URL}"
prefect config set PREFECT_API_AUTH_STRING="${PREFECT_API_AUTH_STRING}" 
prefect config set PREFECT_DEFAULT_RESULT_STORAGE_BLOCK="${PREFECT_DEFAULT_RESULT_STORAGE_BLOCK}"

echo "Starting application..."
python main.py