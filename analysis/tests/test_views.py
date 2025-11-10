"""Tests for analysis views."""
from django.test import TestCase, Client
from django.urls import reverse
from analysis.models import AnalysisJob


class DashboardViewTestCase(TestCase):
    """Test cases for dashboard views."""
    
    def setUp(self):
        self.client = Client()
    
    def test_dashboard_home(self):
        """Test dashboard home page loads."""
        response = self.client.get(reverse('analysis:dashboard'))
        assert response.status_code == 200
        assert 'Analysis Dashboard' in str(response.content)
    
    def test_data_explorer(self):
        """Test data explorer page loads."""
        response = self.client.get(reverse('analysis:data_explorer'))
        assert response.status_code == 200
    
    def test_jobs_list(self):
        """Test jobs list page loads."""
        response = self.client.get(reverse('analysis:jobs_list'))
        assert response.status_code == 200
    
    def test_api_stats(self):
        """Test API stats endpoint."""
        response = self.client.get(reverse('analysis:api_stats'))
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Check response has expected keys
        data = response.json()
        assert 'total_bills' in data
        assert 'total_votes' in data
        assert 'total_people' in data
