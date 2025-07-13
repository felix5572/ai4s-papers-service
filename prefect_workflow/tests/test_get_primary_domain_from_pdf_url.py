import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from workflow_handle_pdf import get_primary_domain_from_pdf_url
import pytest


get_primary_domain_from_pdf_url = get_primary_domain_from_pdf_url.fn # prefect task decorator

class TestGetPrimaryDomainFromPdfUrl:
    """Test cases for get_primary_domain_from_pdf_url function"""
    
    def test_valid_domains(self):
        """Test valid domain mappings"""
        test_cases = [
            ("https://deepmodeling-docs-r2.deepmd.us/test/test_dpgen.pdf", "test"),
            ("https://deepmodeling-docs-r2.deepmd.us/deepmd/guide.pdf", "deepmd"),
            ("https://deepmodeling-docs-r2.deepmd.us/deepmd-kit/tutorial.pdf", "deepmd"),
            ("https://deepmodeling-docs-r2.deepmd.us/abacus/manual.pdf", "abacus"),
            ("https://deepmodeling-docs-r2.deepmd.us/unimol/docs.pdf", "unimol"),
            ("https://deepmodeling-docs-r2.deepmd.us/ai4s/paper.pdf", "ai4s"),
        ]
        
        for url, expected in test_cases:
            assert get_primary_domain_from_pdf_url(url) == expected, f"Failed for URL: {url}"
    
    def test_multilevel_directories(self):
        """Test URLs with multiple directory levels"""
        test_cases = [
            ("https://deepmodeling-docs-r2.deepmd.us/test/subdir/file.pdf", "test"),
            ("https://deepmodeling-docs-r2.deepmd.us/deepmd/v1/api/guide.pdf", "deepmd"),
            ("https://deepmodeling-docs-r2.deepmd.us/abacus/docs/tutorial/basic.pdf", "abacus"),
        ]
        
        for url, expected in test_cases:
            assert get_primary_domain_from_pdf_url(url) == expected, f"Failed for URL: {url}"
    
    def test_root_directory_files(self):
        """Test files in root directory should return unclassified"""
        test_cases = [
            "https://deepmodeling-docs-r2.deepmd.us/file.pdf",
            "https://deepmodeling-docs-r2.deepmd.us/README.pdf",
            "https://deepmodeling-docs-r2.deepmd.us/manual.pdf",
        ]
        
        for url in test_cases:
            assert get_primary_domain_from_pdf_url(url) == "unclassified", f"Failed for URL: {url}"
    
    def test_root_directory(self):
        """Test root directory URLs"""
        test_cases = [
            "https://deepmodeling-docs-r2.deepmd.us/",
            "https://deepmodeling-docs-r2.deepmd.us",
        ]
        
        for url in test_cases:
            assert get_primary_domain_from_pdf_url(url) == "unclassified", f"Failed for URL: {url}"
    
    def test_unknown_directories(self):
        """Test unknown directories should return unknown"""
        test_cases = [
            "https://deepmodeling-docs-r2.deepmd.us/unknown-dir/file.pdf",
            "https://deepmodeling-docs-r2.deepmd.us/random/document.pdf",
            "https://deepmodeling-docs-r2.deepmd.us/other-project/guide.pdf",
        ]
        
        for url in test_cases:
            assert get_primary_domain_from_pdf_url(url) == "unknown", f"Failed for URL: {url}"
    
    def test_directory_with_trailing_slash(self):
        """Test directories ending with slash"""
        test_cases = [
            ("https://deepmodeling-docs-r2.deepmd.us/test/", "test"),
            ("https://deepmodeling-docs-r2.deepmd.us/deepmd/", "deepmd"),
        ]
        
        for url, expected in test_cases:
            assert get_primary_domain_from_pdf_url(url) == expected, f"Failed for URL: {url}"
    
    def test_different_domains(self):
        """Test with different domain names"""
        test_cases = [
            ("https://another-domain.com/test/file.pdf", "test"),
            ("http://example.org/deepmd/guide.pdf", "deepmd"),
            ("https://docs.company.net/abacus/manual.pdf", "abacus"),
        ]
        
        for url, expected in test_cases:
            assert get_primary_domain_from_pdf_url(url) == expected, f"Failed for URL: {url}"
    
    @pytest.mark.parametrize("url,expected", [
        ("https://deepmodeling-docs-r2.deepmd.us/test/test_dpgen.pdf", "test"),
        ("https://deepmodeling-docs-r2.deepmd.us/file.pdf", "unclassified"),
        ("https://deepmodeling-docs-r2.deepmd.us/unknown/file.pdf", "unknown"),
    ])
    def test_parametrized_cases(self, url, expected):
        """Parametrized test cases"""
        assert get_primary_domain_from_pdf_url(url) == expected