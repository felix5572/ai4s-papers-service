from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import io
from unittest.mock import patch, AsyncMock
from .models import Paper

class PaperAPITest(TestCase):
    
    def setUp(self):
        """Prepare test data"""
        self.client = Client()
        
        # Create a simple PDF-like content for testing
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF'
        
        # Test metadata
        self.test_metadata = {
            'title': 'Test Paper for PDF Upload',
            'authors': 'Test Author, Another Author',
            'year': 2024,
            'primary_domain': 'deepmd',
            'journal': 'Test Journal',
            'abstract': 'This is a test abstract for PDF upload functionality.',
            'keywords': 'test, pdf, upload',
            'doi': '10.1000/test.doi',
            'url': 'https://test.example.com',
            'arxiv_id': 'test.1234'
        }
    
    def test_list_papers(self):
        """Test getting list of all papers"""
        print("\n=== Test: List All Papers ===")
        
        # Create test paper
        Paper.objects.create( # type: ignore
            title="Test Paper",
            authors="Test Author",
            year=2024,
            primary_domain="deepmd"
        )
        
        response = self.client.get('/api/papers')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Test Paper')
    
    def test_create_paper_json(self):
        """Test creating paper with JSON metadata only"""
        print("\n=== Test: Create Paper (JSON) ===")
        
        paper_data = {
            'title': 'JSON Test Paper',
            'authors': 'JSON Author',
            'year': 2024,
            'primary_domain': 'abacus',
            'journal': 'JSON Journal'
        }
        
        response = self.client.post('/api/papers',
                                  json.dumps(paper_data),
                                  content_type='application/json')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['title'], 'JSON Test Paper')
        self.assertEqual(data['primary_domain'], 'abacus')
        
        # Verify in database
        paper = Paper.objects.get(title='JSON Test Paper') # type: ignore
        self.assertEqual(paper.authors, 'JSON Author')
    
    def test_upload_paper_with_pdf_only(self):
        """Test uploading paper with PDF file only (sync)"""
        print("\n=== Test: Upload Paper with PDF (Sync) ===")
        
        pdf_file = SimpleUploadedFile(
            "test_paper.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = self.test_metadata.copy()
        form_data['pdf_file'] = pdf_file
        
        response = self.client.post('/api/papers/upload', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['title'], 'Test Paper for PDF Upload')
        self.assertEqual(data['pdf_filename'], 'test_paper.pdf')
        
        # Verify PDF content saved
        paper = Paper.objects.get(title='Test Paper for PDF Upload') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertEqual(len(paper.pdf_content), len(self.test_pdf_content))
    
    def test_upload_paper_with_markdown(self):
        """Test uploading paper with both PDF and Markdown files"""
        print("\n=== Test: Upload Paper with PDF and Markdown ===")
        
        pdf_file = SimpleUploadedFile(
            "test_paper.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        markdown_content = "# Test Paper\n\nThis is test markdown content.\n\n## Abstract\n\nTest abstract here."
        markdown_file = SimpleUploadedFile(
            "test_paper.md",
            markdown_content.encode('utf-8'),
            content_type="text/markdown"
        )
        
        form_data = self.test_metadata.copy()
        form_data['title'] = 'Paper with Both Files'
        form_data['pdf_file'] = pdf_file
        form_data['markdown_file'] = markdown_file
        
        response = self.client.post('/api/papers/upload', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Verify both files saved
        paper = Paper.objects.get(title='Paper with Both Files') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertIsNotNone(paper.markdown_content)
        self.assertIn('Test Paper', paper.markdown_content)
        self.assertEqual(paper.markdown_filename, 'test_paper.md')
    
    @patch('papers_db.api.parse_pdf_with_modal_async')
    def test_upload_parse_pdf_success(self, mock_parse):
        """Test PDF upload with successful async parsing"""
        print("\n=== Test: PDF Upload with Parsing (Success) ===")
        
        # Mock successful parsing
        mock_parse.return_value = "# Parsed Content\n\nThis is parsed markdown from PDF."
        
        pdf_file = SimpleUploadedFile(
            "parse_test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = self.test_metadata.copy()
        form_data['title'] = 'PDF Parse Test'
        form_data['pdf_file'] = pdf_file
        
        response = self.client.post('/api/papers/upload-parse', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Verify parsing was called
        mock_parse.assert_called_once()
        
        # Verify paper saved with markdown
        paper = Paper.objects.get(title='PDF Parse Test') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertIsNotNone(paper.markdown_content)
        self.assertIn('Parsed Content', paper.markdown_content)
    
    @patch('papers_db.api.parse_pdf_with_modal_async')
    def test_upload_parse_pdf_failure(self, mock_parse):
        """Test PDF upload with failed parsing"""
        print("\n=== Test: PDF Upload with Parsing (Failed) ===")
        
        # Mock failed parsing
        mock_parse.return_value = ""
        
        pdf_file = SimpleUploadedFile(
            "parse_fail_test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = self.test_metadata.copy()
        form_data['title'] = 'PDF Parse Fail Test'
        form_data['pdf_file'] = pdf_file
        
        response = self.client.post('/api/papers/upload-parse', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Verify paper saved but no markdown
        paper = Paper.objects.get(title='PDF Parse Fail Test') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertIsNone(paper.markdown_content)
    
    def test_upload_parse_invalid_file(self):
        """Test PDF upload with non-PDF file"""
        print("\n=== Test: PDF Upload with Invalid File ===")
        
        # Try to upload a text file as PDF
        text_file = SimpleUploadedFile(
            "not_a_pdf.txt",
            b"This is not a PDF file",
            content_type="text/plain"
        )
        
        form_data = self.test_metadata.copy()
        form_data['pdf_file'] = text_file
        
        response = self.client.post('/api/papers/upload-parse', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        # Should return error for non-PDF file
        self.assertNotEqual(response.status_code, 200) # type: ignore

    @patch('papers_db.api.httpx.AsyncClient')
    def test_direct_file_upload_to_modal(self, mock_client):
        """Test direct file upload to Modal API (new method)"""
        print("\n=== Test: Direct File Upload to Modal API ===")
        
        # Mock the async HTTP client with proper return values
        mock_response = AsyncMock()
        mock_response.status_code = 200
        # Mock headers properly
        mock_response.headers = {'content-type': 'application/json'}
        # Mock json method to return the expected data as coroutine
        mock_response.json = AsyncMock(return_value={
            "success": True,
            "markdown": "# Direct Upload Test\n\nParsed content from direct upload."
        })
        
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_context)
        mock_context.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_context
        
        pdf_file = SimpleUploadedFile(
            "direct_upload_test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = self.test_metadata.copy()
        form_data['title'] = 'Direct Upload Test'
        form_data['pdf_file'] = pdf_file
        
        response = self.client.post('/api/papers/upload-parse', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Verify the HTTP client was called with correct parameters
        mock_client.assert_called_once_with(timeout=300.0)
        
        # Verify paper saved with parsed markdown
        paper = Paper.objects.get(title='Direct Upload Test') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertIsNotNone(paper.markdown_content)
        self.assertIn('Direct Upload Test', paper.markdown_content)

    @patch('papers_db.api.httpx.AsyncClient')
    def test_modal_api_error_handling(self, mock_client):
        """Test error handling when Modal API fails"""
        print("\n=== Test: Modal API Error Handling ===")
        
        # Mock API failure with proper response
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = "Internal Server Error"
        
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_context)
        mock_context.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_context
        
        pdf_file = SimpleUploadedFile(
            "error_test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = self.test_metadata.copy()
        form_data['title'] = 'Error Test Paper'
        form_data['pdf_file'] = pdf_file
        
        response = self.client.post('/api/papers/upload-parse', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        # Paper should still be saved even if parsing fails
        paper = Paper.objects.get(title='Error Test Paper') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertIsNone(paper.markdown_content)  # No markdown due to parsing failure

    @patch('papers_db.api.httpx.AsyncClient')
    def test_modal_api_timeout_handling(self, mock_client):
        """Test timeout handling for Modal API"""
        print("\n=== Test: Modal API Timeout Handling ===")
        
        # Mock timeout exception properly
        from httpx import TimeoutException
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_context)
        mock_context.post = AsyncMock(side_effect=TimeoutException("Request timeout"))
        mock_client.return_value = mock_context
        
        pdf_file = SimpleUploadedFile(
            "timeout_test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        form_data = self.test_metadata.copy()
        form_data['title'] = 'Timeout Test Paper'
        form_data['pdf_file'] = pdf_file
        
        response = self.client.post('/api/papers/upload-parse', form_data)
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        # Paper should still be saved even if parsing times out
        paper = Paper.objects.get(title='Timeout Test Paper') # type: ignore
        self.assertIsNotNone(paper.pdf_content)
        self.assertIsNone(paper.markdown_content)  # No markdown due to timeout


# CURL Commands for Manual Testing
"""
=== CURL Commands for Testing ===

1. List all papers:
curl -X GET "https://ai4s-papers-service.deepmd.us/api/papers" \
  -H "Accept: application/json"

2. Create paper with JSON metadata:
curl -X POST "https://ai4s-papers-service.deepmd.us/api/papers" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Paper via JSON",
    "authors": "JSON Author",
    "year": 2024,
    "primary_domain": "deepmd",
    "journal": "Test Journal",
    "abstract": "Test abstract"
  }'

3. Upload paper with PDF file (sync):
curl -X POST "https://ai4s-papers-service.deepmd.us/api/papers/upload" \
  -F "title=Test Paper via Upload" \
  -F "authors=Upload Author" \
  -F "year=2024" \
  -F "primary_domain=deepmd" \
  -F "journal=Upload Journal" \
  -F "abstract=Upload test abstract" \
  -F "pdf_file=@/path/to/your/paper.pdf"

4. Upload PDF with async parsing (NEW: Direct File Upload):
curl -X POST "https://ai4s-papers-service.deepmd.us/api/papers/upload-parse" \
  -F "title=Test Paper with Direct Upload Parsing" \
  -F "authors=Parse Author" \
  -F "year=2024" \
  -F "primary_domain=deepmd" \
  -F "journal=Parse Journal" \
  -F "abstract=This paper will be parsed using direct file upload" \
  -F "keywords=parsing, test, async, direct-upload" \
  -F "doi=10.1000/parse.test" \
  -F "pdf_file=@/path/to/your/paper.pdf"

5. Upload with both PDF and Markdown:
curl -X POST "https://ai4s-papers-service.deepmd.us/api/papers/upload" \
  -F "title=Paper with Both Files" \
  -F "authors=Both Files Author" \
  -F "year=2024" \
  -F "primary_domain=abacus" \
  -F "pdf_file=@/path/to/paper.pdf" \
  -F "markdown_file=@/path/to/paper.md"

6. Test FastGPT API integration:
curl -X POST "https://ai4s-papers-service.deepmd.us/api/fastgpt/v1/file/list" \
  -H "Content-Type: application/json" \
  -d '{"parentId":"","searchKey":""}'

=== Local Testing (Development) ===

Replace "https://ai4s-papers-service.deepmd.us" with "http://localhost:8000" for local testing:

curl -X POST "http://localhost:8000/api/papers/upload-parse" \
  -F "title=Local Test Paper" \
  -F "authors=Local Author" \
  -F "year=2024" \
  -F "primary_domain=test" \
  -F "pdf_file=@/path/to/test.pdf"

=== Testing with Sample PDF ===

# Create a simple test PDF file:
echo '%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000074 00000 n 
0000000120 00000 n 
0000000179 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
274
%%EOF' > test.pdf

# Then use this test.pdf in your curl commands
"""
