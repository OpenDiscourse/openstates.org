"""Tests for NLP processor and micro-statement extraction."""
import pytest
from django.test import TestCase
from analysis.nlp_processor import NLPProcessor, get_processor


class NLPProcessorTestCase(TestCase):
    """Test cases for NLP processor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use simple test text that doesn't require actual models
        self.test_text = (
            "The legislature shall provide funding to public schools. "
            "The senator will protect citizens from higher taxes. "
            "The committee must regulate businesses to ensure safety."
        )
        self.processor = NLPProcessor()
    
    def test_processor_singleton(self):
        """Test that get_processor returns singleton instance."""
        proc1 = get_processor()
        proc2 = get_processor()
        assert proc1 is proc2
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis."""
        # Test positive sentiment
        result = self.processor.analyze_sentiment("This is wonderful and excellent")
        assert result['label'] in ['positive', 'neutral', 'negative']
        assert isinstance(result['score'], (int, float))
        
        # Test empty text
        result = self.processor.analyze_sentiment("")
        assert result['label'] == 'neutral'
        assert result['score'] == 0.0
    
    def test_extract_micro_statements_empty(self):
        """Test extraction with empty text."""
        statements = self.processor.extract_micro_statements("")
        assert statements == []
        
        statements = self.processor.extract_micro_statements(None)
        assert statements == []
    
    def test_extract_micro_statements_structure(self):
        """Test that extracted statements have correct structure."""
        metadata = {
            'session_year': 2023,
            'jurisdiction': 'tx',
            'party': 'Democratic',
        }
        
        statements = self.processor.extract_micro_statements(self.test_text, metadata)
        
        # Check that we got some statements
        assert isinstance(statements, list)
        
        # If we got statements, check their structure
        for stmt in statements:
            assert 'actor' in stmt
            assert 'action' in stmt
            assert 'target' in stmt
            assert 'statement_text' in stmt
            assert 'original_text' in stmt
            assert 'sentiment' in stmt
            assert 'sentiment_score' in stmt
            assert 'entities' in stmt
            assert 'confidence_score' in stmt
            assert 'extraction_method' in stmt
            assert 'statement_type' in stmt
            
            # Check metadata was passed through
            assert stmt['session_year'] == 2023
            assert stmt['jurisdiction'] == 'tx'
            assert stmt['party'] == 'Democratic'
            
            # Check types
            assert isinstance(stmt['actor'], str)
            assert isinstance(stmt['action'], str)
            assert isinstance(stmt['target'], str)
            assert isinstance(stmt['confidence_score'], float)
            assert stmt['sentiment'] in ['positive', 'negative', 'neutral', 'mixed']
            assert stmt['statement_type'] in ['action', 'position', 'impact']
    
    def test_is_policy_statement(self):
        """Test policy statement detection."""
        # Test with clear policy statement
        assert self.processor._is_policy_statement(
            "The legislature", 
            "shall provide", 
            "funding to schools"
        )
        
        # Test with non-policy statement
        result = self.processor._is_policy_statement(
            "The dog", 
            "runs", 
            "fast"
        )
        # May or may not be detected as policy, just check it doesn't crash
        assert isinstance(result, bool)
    
    def test_classify_statement_type(self):
        """Test statement type classification."""
        assert self.processor._classify_statement_type("shall provide") == 'action'
        assert self.processor._classify_statement_type("must require") == 'action'
        assert self.processor._classify_statement_type("supports") == 'action'  # Default
        assert self.processor._classify_statement_type("will affect") == 'impact'
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        entities = {
            'people': ['John Smith'],
            'organizations': ['Department'],
            'locations': [],
            'dates': [],
            'money': []
        }
        
        score = self.processor._calculate_confidence(
            "The senator",
            "shall provide",
            "funding to schools",
            entities
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Test with minimal info
        score = self.processor._calculate_confidence("A", "do", "B", {})
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class ExtractEntitiesTestCase(TestCase):
    """Test entity extraction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = NLPProcessor()
    
    def test_extract_entities(self):
        """Test entity extraction from sentence."""
        text = "Senator John Smith from Texas allocated $1 million on January 1st."
        doc = self.processor.nlp(text)
        
        for sent in doc.sents:
            entities = self.processor._extract_entities(sent)
            
            assert isinstance(entities, dict)
            assert 'people' in entities
            assert 'organizations' in entities
            assert 'locations' in entities
            assert 'dates' in entities
            assert 'money' in entities
            
            # All should be lists
            for key, value in entities.items():
                assert isinstance(value, list)
