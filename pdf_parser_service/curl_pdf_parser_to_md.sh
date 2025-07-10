curl -X POST https://yfb222333--pdf-parser-parse-pdf-upload.modal.run \
  -F "file=@../bks/test_dpgen.pdf" \
  -F "engine=marker"  \
  | jq -r '.data.markdown' > test_dpgen.md