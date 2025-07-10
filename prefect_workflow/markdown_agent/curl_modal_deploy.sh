curl -X POST "https://yfb222333--paper-metadata-agent-analyze-paper-raw-llm-output.modal.run" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# AI Research Paper\nAuthors: Alice, Bob\nYear: 2024\nThis is a test paper about artificial intelligence."
  }'