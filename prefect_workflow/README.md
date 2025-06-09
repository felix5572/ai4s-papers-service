# Prefect Workflow

Simple Prefect workflow for processing customers.

## Local Development

```bash
# Install dependencies
pip install -e .

# export PREFECT_API_AUTH_STRING=${PREFECT_API_AUTH_STRING}
# export PREFECT_API_URL=${PREFECT_API_URL}

# Run workflow directly
python prefect_getting_started.py

# Start service
python main.py
```

## Deployment

Deploy to Zeabur by uploading this folder or connecting to Git repository. 