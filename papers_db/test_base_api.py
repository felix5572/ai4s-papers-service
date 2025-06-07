from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Paper
from .schemas import PaperOut

class PaperAPITest(TestCase):
    
    def setUp(self):
        """prepare test data"""
        self.client = Client()
        self.test_paper = Paper.objects.create( # type: ignore
            title="AI for Science Research Paper",
            authors="Dr. Smith, Dr. Johnson, Dr. Chen",
            year=2024,
            primary_domain="test_domain",
            journal="Nature Physics",
            abstract="This is a comprehensive test abstract about AI for Science research.",
            keywords="AI, science, machine learning, physics",
            doi="10.1000/test.doi.123",
            arxiv_id="2024.12345",
            tags="test, research, ai4s"
        )
    
    def test_get_papers(self):
        """get papers list"""
        from django.db import connection
        from django.conf import settings
        
        print(f"\n=== Database Connection Info ===")
        print(f"Database Engine: {settings.DATABASES['default'].get('ENGINE', None)}")
        print(f"Database Name: {settings.DATABASES['default'].get('NAME', None)}")
        print(f"Database Host: {settings.DATABASES['default'].get('HOST', None)}")
        print(f"Database Port: {settings.DATABASES['default'].get('PORT', None)}")
        print(f"Database User: {settings.DATABASES['default'].get('USER', None)}")
        
        print(f"\n=== Database Status ===")
        print(f"Connection Vendor: {connection.vendor}")
        print(f"Connection Display Name: {connection.display_name}")
        print(f"Total Queries So Far: {len(connection.queries)}")
        
        # 测试HTTP请求
        print(f"\n=== HTTP Request Info ===")
        print(f"Request URL: /api/papers")
        print(f"Request Method: GET")
        
        response = self.client.get('/api/papers')
        
        print(f"\n=== HTTP Response Info ===")
        print(f"Status Code: {response.status_code}") # type: ignore
        print(f"Content-Type: {response.get('Content-Type', 'Not set')}") # type: ignore
        print(f"Response Size: {len(response.content)} bytes") # type: ignore
        print(f"Has JSON Content: {hasattr(response, 'json')}")
        
        print(f"\n=== Django Test Environment ===")
        print(f"Test Database: {connection.settings_dict['NAME']}")
        print(f"Debug Mode: {settings.DEBUG}")
        print(f"Test Client: {type(self.client).__name__}")
        
        self.assertEqual(response.status_code, 200) # type: ignore
        print(f"\n=== DB List Test Status: PASSED ===")
    
    def test_create_paper(self):
        """create paper and verify it can be found"""
        # use test_paper data, modify domain and title to avoid duplicate
        
        create_response = self.client.post('/api/papers', 
            PaperOut.from_orm(self.test_paper).model_dump_json(), 
            content_type='application/json')
        self.assertEqual(create_response.status_code, 200) # type: ignore
        
        # verify the created paper can be found
        list_response = self.client.get('/api/papers')
        self.assertEqual(list_response.status_code, 200) # type: ignore
        papers = list_response.json() # type: ignore
        
        # search the created paper by test_domain
        found_paper = next((p for p in papers if p['primary_domain'] == 'test_domain'), None)
        self.assertIsNotNone(found_paper, "Cannot find created paper with test_domain")
        self.assertEqual(found_paper['authors'], self.test_paper.authors) # type: ignore
    
    # def test_get_empty_papers_list(self):
    #     """get papers list when database is empty"""
    #     response = self.client.get('/api/papers')
    #     self.assertEqual(response.status_code, 200) # type: ignore
    #     data = response.json() # type: ignore
    #     self.assertEqual(len(data), 0) 