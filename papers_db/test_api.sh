# test api

# test get papers
curl -X GET http://localhost:8000/api/papers

curl -X GET https://ai4s-papers-service.deepmd.us/api/papers

curl -X GET https://ai4s-papers-service.deepmd.us/api/papers

# curl -X POST https://ai4s-papers-service.deepmd.us/v1/file/list -H "Content-Type: application/json" -d '{}'

# test create paper
curl -X POST http://localhost:8000/api/papers \
  -H "Content-Type: application/json" \
  -d '{"title": "test", "authors": "test", "year": 2024, "primary_domain": "test"}'

curl -X POST http://localhost:8000/api/papers/upload \
  -F "title=Complete Upload Test" \
  -F "authors=Dr. Upload, Prof. File" \
  -F "year=2024" \
  -F "primary_domain=test" \
  -F "journal=Upload Journal" \
  -F "abstract=This is a test paper with file upload" \
  -F "keywords=upload, file, test" \
  -F "doi=10.1000/upload.2024" \
  -F "arxiv_id=2024.upload" \
  -F "tags=upload, file, complete" \
  -F "pdf_file=@test_DeePMD-kit.pdf" \
  -F "markdown_file=@test_DeePMD-kit.md"

curl -X POST localhost:8000/api/fastgpt/v1/file/list \
  -H "Content-Type: application/json" -d '{}'

# curl -X POST https://ai4s-papers-service.deepmd.us/v1/file/list -H "Content-Type: application/json" -d '{}'

curl -X POST localhost:8000/api/fastgpt/v1/file/list \
  -H "Content-Type: application/json" -d '{"parentId":"test","searchKey":""}'


# 3. 获取具体论文内容（假设从上面得到paper_1）
curl "localhost:8000/api/file/v1/file/content?id=paper_7"

# 4. 测试不存在的论文（应该报错）
curl "localhost:8000/api/file/v1/file/content?id=paper_99999"

# 5. 如果论文有PDF，可以直接访问PDF
curl "localhost:8000/api/file/pdf/7" --output test.pdf

curl "localhost:8000/api/file/v1/file/detail?id=paper_7"

# # # test get papers again
# # curl -X GET http://localhost:8000/api/papers

# # test complete paper with all fields
# curl -X POST http://localhost:8000/api/papers \
#   -H "Content-Type: application/json" \
#   -d '{
#     "title": "Complete Test Paper",
#     "authors": "Dr. Test, Prof. Example",
#     "year": 2024,
#     "primary_domain": "test",
#     "journal": "Test Journal",
#     "abstract": "This is a test paper abstract",
#     "keywords": "test, paper, api",
#     "doi": "10.1000/test.2024",
#     "arxiv_id": "2024.test",
#     "tags": "test, complete"
#   }'
