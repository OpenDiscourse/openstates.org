"""Tests for analysis models."""
import pytest
from django.test import TestCase
from analysis.models import (
    AnalysisJob,
    BillTextAnalysis,
    LegislatorProfile,
    VoteAnalysis,
    DataIngestionLog,
)


class AnalysisJobTestCase(TestCase):
    """Test cases for AnalysisJob model."""
    
    def test_create_analysis_job(self):
        """Test creating an analysis job."""
        job = AnalysisJob.objects.create(
            job_type='nlp',
            status='pending',
            parameters={'jurisdiction': 'tx'},
        )
        
        assert job.id is not None
        assert job.job_type == 'nlp'
        assert job.status == 'pending'
        assert job.parameters == {'jurisdiction': 'tx'}
        assert str(job).startswith('NLP Analysis')
    
    def test_job_progress(self):
        """Test job progress tracking."""
        job = AnalysisJob.objects.create(
            job_type='nlp',
            status='running',
            total_items=100,
            processed_items=50,
        )
        
        assert job.total_items == 100
        assert job.processed_items == 50


class DataIngestionLogTestCase(TestCase):
    """Test cases for DataIngestionLog model."""
    
    def test_create_ingestion_log(self):
        """Test creating an ingestion log."""
        log = DataIngestionLog.objects.create(
            database_type='postgresql',
            database_host='localhost',
            database_name='testdb',
            jurisdictions=['tx', 'ca'],
            status='running',
        )
        
        assert log.id is not None
        assert log.database_type == 'postgresql'
        assert log.jurisdictions == ['tx', 'ca']
        assert log.status == 'running'
        assert 'Ingestion' in str(log)
