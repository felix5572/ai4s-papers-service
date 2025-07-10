#!/bin/bash
source ../.env


# 临时设置 secrets 并部署
echo "$PREFECT_API_AUTH_STRING" | npx wrangler secret put PREFECT_API_AUTH_STRING

PREFECT_FLOW_DEPLOYMENT_ID=$(prefect deployment inspect workflow-handle-pdf-to-db-and-fastgpt/zeabur-deploy-workflow-handle-pdf-to-db-and-fastgpt | python3 -c "import sys,ast; print(ast.literal_eval(sys.stdin.read())['id'])")

echo "PREFECT_FLOW_DEPLOYMENT_ID: ${PREFECT_FLOW_DEPLOYMENT_ID}"
# npx wrangler deploy --var PREFECT_FLOW_DEPLOYMENT_ID=${PREFECT_FLOW_DEPLOYMENT_ID}
npx wrangler deploy 