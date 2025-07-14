curl -u "${PREFECT_API_AUTH_STRING}" "https://yusvyffgaqjc.sealosbja.site/api/health"

curl -X POST "${PREFECT_API_URL}/deployments/ec4e26f8-9fd7-466d-bbe4-8f33628806ea/create_flow_run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n "${PREFECT_API_AUTH_STRING}" | base64)" \
  -d '{
    "parameters": {
      "s3_object_url": "https://deepmodeling-docs-r2.deepmd.us/deepmd-kit/dpgen.pdf"
    }
  }'