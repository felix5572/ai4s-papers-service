 # DOCs      https://docs.prefect.io/v3/api-ref/rest-api/server/flow-runs/create-flow-run
 # get all flows
 curl -X POST "${PREFECT_API_URL}/flows/filter"   -H "Content-Type: application/json"   -H "x-prefect-api-version: 0.8.4"   -d '{}'

curl -X POST "${PREFECT_API_URL}/flows/filter" \
  --user "${PREFECT_API_AUTH_STRING}" \
  -H "Content-Type: application/json" \
  -H "x-prefect-api-version: 0.8.4" \
  -d '{}'

# create flow run

    # "flow_id": "a4e97945-6fc5-4380-a6a5-5ad6aa0a7296",

curl -X POST "${PREFECT_API_URL}/flow_runs/" \
  --user "${PREFECT_API_AUTH_STRING}" \
  -H "Content-Type: application/json" \
  -H "x-prefect-api-version: 0.8.4" \
  -d '{
    "flow_id": "f6cbb3f8-c7a5-4943-ba1d-ad4cc2a2fb5a",
    "name": "api-trigger-'$(date +%s)'",
    "tags": ["api-trigger"],
    "work_pool_name": "pc-local-work-pool"
  }'