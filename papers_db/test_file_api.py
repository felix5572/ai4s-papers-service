from django.test import TestCase, Client
import json
from .models import Paper

class FileAPITest(TestCase):
    
    def setUp(self):
        """Prepare test data"""
        self.client = Client()
        
        # Create test papers for different domains
        self.paper1 = Paper.objects.create( # type: ignore
            title="DeepMD Test Paper",
            authors="Author A, Author B",
            year=2024,
            primary_domain="deepmd",
            journal="Nature Physics",
            abstract="This is a test abstract for DeepMD.",
            keywords="deepmd, machine learning",
            tags="test, deepmd"
        )
        
        self.paper2 = Paper.objects.create( # type: ignore
            title="ABACUS Test Paper",
            authors="Author C, Author D",
            year=2023,
            primary_domain="abacus",
            journal="Physical Review B",
            abstract="This is a test abstract for ABACUS.",
            keywords="abacus, dft, first-principles",
            tags="test, abacus"
        )
    
    def test_list_domains(self):
        """Test getting list of domains (root level)"""
        print("\n=== Test: List Domains ===")
        
        response = self.client.post('/api/file/v1/file/list',
                                  json.dumps({"parentId": "", "searchKey": ""}),
                                  content_type='application/json')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['success'])
        self.assertIn('files', data['data'])
        
        # Check if we have the expected domains
        files = data['data']['files']
        domain_names = [f['id'] for f in files]
        self.assertIn('deepmd', domain_names)
        self.assertIn('abacus', domain_names)
    
    def test_list_papers_in_domain(self):
        """Test getting papers in specific domain"""
        print("\n=== Test: List Papers in Domain ===")
        
        response = self.client.post('/api/file/v1/file/list',
                                  json.dumps({"parentId": "deepmd", "searchKey": ""}),
                                  content_type='application/json')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['success'])
        
        files = data['data']['files']
        self.assertEqual(len(files), 1)  # Should have one paper in deepmd domain
        
        paper_file = files[0]
        self.assertEqual(paper_file['type'], 'file')
        self.assertIn('DeepMD Test Paper', paper_file['name'])
        self.assertEqual(paper_file['parentId'], 'deepmd')
    
    def test_search_papers(self):
        """Test searching papers by keyword"""
        print("\n=== Test: Search Papers ===")
        
        response = self.client.post('/api/file/v1/file/list',
                                  json.dumps({"parentId": "abacus", "searchKey": "ABACUS"}),
                                  content_type='application/json')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        files = data['data']['files']
        self.assertEqual(len(files), 1)
        self.assertIn('ABACUS Test Paper', files[0]['name'])
    
    def test_get_file_content_with_markdown(self):
        """Test getting file content with markdown"""
        print("\n=== Test: Get File Content (Markdown) ===")
        
        # Create a paper with markdown content
        paper_with_md = Paper.objects.create( # type: ignore
            title="Markdown Test Paper",
            authors="Author MD",
            year=2024,
            primary_domain="test",
            markdown_content="# Test Markdown\n\nThis is test content."
        )
        
        paper_id = f"paper_{paper_with_md.id}"
        response = self.client.get(f'/api/file/v1/file/content?id={paper_id}')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'Markdown Test Paper')
        self.assertIn('Test Markdown', data['data']['content'])
        self.assertIsNone(data['data']['previewUrl'])
    
    def test_get_file_content_with_abstract_only(self):
        """Test getting file content with only abstract"""
        print("\n=== Test: Get File Content (Abstract Only) ===")
        
        paper_id = f"paper_{self.paper1.id}"  # This paper has abstract but no markdown
        response = self.client.get(f'/api/file/v1/file/content?id={paper_id}')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'DeepMD Test Paper')
        self.assertIn('test abstract for DeepMD', data['data']['content'])
    
    def test_get_file_content_not_found(self):
        """Test getting content for non-existent paper"""
        print("\n=== Test: Get File Content (Not Found) ===")
        
        response = self.client.get('/api/file/v1/file/content?id=paper_99999')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        # Should return 404 or 500, Django will handle the error
        self.assertNotEqual(response.status_code, 200) # type: ignore
    
    def test_get_file_detail_paper(self):
        """Test getting paper detail"""
        print("\n=== Test: Get Paper Detail ===")
        
        paper_id = f"paper_{self.paper1.id}"
        response = self.client.get(f'/api/file/v1/file/detail?id={paper_id}')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['success'])
        
        detail = data['data']
        # Check PaperOut fields
        self.assertEqual(detail['title'], 'DeepMD Test Paper')
        self.assertEqual(detail['year'], 2024)
        self.assertEqual(detail['authors'], 'Author A, Author B')
        self.assertEqual(detail['primary_domain'], 'deepmd')
        # Check added fields
        self.assertEqual(detail['parentId'], 'deepmd')
        self.assertEqual(detail['type'], 'file')
    
    def test_get_file_detail_domain(self):
        """Test getting domain detail"""
        print("\n=== Test: Get Domain Detail ===")
        
        response = self.client.get('/api/file/v1/file/detail?id=deepmd')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        self.assertEqual(response.status_code, 200) # type: ignore
        
        data = response.json() # type: ignore
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['success'])
        
        detail = data['data']
        self.assertEqual(detail['id'], 'deepmd')
        self.assertIsNone(detail['parentId'])
        self.assertEqual(detail['type'], 'folder')
        self.assertIn('(1篇论文)', detail['name'])
    
    def test_get_file_detail_not_found(self):
        """Test getting detail for non-existent item"""
        print("\n=== Test: Get Detail (Not Found) ===")
        
        response = self.client.get('/api/file/v1/file/detail?id=paper_99999')
        
        print(f"Status Code: {response.status_code}") # type: ignore
        # Should return 404 or 500, Django will handle the error
        self.assertNotEqual(response.status_code, 200) # type: ignore 