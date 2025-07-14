#%%

# curl --location --request POST 'http://localhost:3000/api/core/dataset/collection/create/text' \
curl --location --request POST "${FASTGPT_WEBURL}/api/core/dataset/collection/create/text" \
--header "Authorization: Bearer ${FASTGPT_DEVELOPER_API_KEY}" \
--header 'Content-Type: application/json' \
--data-raw '{
    "text":"Example text. For testing. It should be a doc related to dpgen",
    "datasetId":"684897a43609eeebb2bc7391",
    "parentId": null,
    "name":"test_training.md",
    "trainingType": "chunk",
    "chunkSettingMode": "auto",
    "metadata":{}
}'


curl --location --request POST "${FASTGPT_WEBURL}/api/core/dataset/collection/create/link" \
--header "Authorization: Bearer ${FASTGPT_DEVELOPER_API_KEY}" \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "test_DeePMD-kit.md",
    "link":"https://pub-ade6b229d96a43a18ad0d4f7efe93a58.r2.dev/test_DeePMD-kit.md",
    "datasetId": "684897a43609eeebb2bc7391",
    "parentId": null,
    "trainingType": "chunk",
    "chunkSettingMode": "auto",
    "metadata":{}
}'

curl --location --request POST "${FASTGPT_WEBURL}/api/core/dataset/collection/create/localFile" \
    --header "Authorization: Bearer ${FASTGPT_DEVELOPER_API_KEY}" \
    --form 'file=@"./test_dpgen.md"' \
    --form 'data="{
        \"datasetId\": \"6873ef82deecd959acb461fb\",
        \"parentId\": null,
        \"trainingType\": \"chunk\",
        \"chunkSettingMode\": \"auto\",
        \"metadata\": {}
    }"'