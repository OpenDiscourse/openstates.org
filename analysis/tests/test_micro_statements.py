"""Tests for MicroStatement model."""
import pytest
from django.test import TestCase
from analysis.models import MicroStatement


class MicroStatementTestCase(TestCase):
    """Test cases for MicroStatement model."""
    
    def test_create_micro_statement(self):
        """Test creating a micro-statement without bill reference."""
        statement = MicroStatement.objects.create(
            actor="The legislature",
            action="shall provide",
            target="funding to schools",
            statement_text="The legislature shall provide funding to schools",
            original_text="The legislature shall provide funding to schools.",
            statement_type='action',
            sentiment='positive',
            sentiment_score=0.8,
            session_year=2023,
            jurisdiction='tx',
            party='Democratic',
            entities={'people': [], 'organizations': ['legislature']},
            confidence_score=0.85,
            extraction_method='spacy_svo',
        )
        
        assert statement.id is not None
        assert statement.actor == "The legislature"
        assert statement.action == "shall provide"
        assert statement.target == "funding to schools"
        assert statement.sentiment == 'positive'
        assert statement.session_year == 2023
        assert statement.jurisdiction == 'tx'
        assert str(statement) == "The legislature shall provide funding to schools"
    
    def test_statement_types(self):
        """Test different statement types."""
        for stmt_type, label in MicroStatement.STATEMENT_TYPES:
            statement = MicroStatement.objects.create(
                actor="Actor",
                action="action",
                target="target",
                statement_text="test",
                statement_type=stmt_type,
            )
            assert statement.statement_type == stmt_type
    
    def test_sentiment_choices(self):
        """Test different sentiment values."""
        for sentiment, label in MicroStatement.SENTIMENT_CHOICES:
            statement = MicroStatement.objects.create(
                actor="Actor",
                action="action",
                target="target",
                statement_text="test",
                sentiment=sentiment,
            )
            assert statement.sentiment == sentiment
    
    def test_metadata_fields(self):
        """Test metadata fields for binning."""
        statement = MicroStatement.objects.create(
            actor="Senator",
            action="votes for",
            target="bill",
            statement_text="Senator votes for bill",
            session_year=2023,
            jurisdiction='ca',
            district='District 10',
            party='Republican',
        )
        
        assert statement.session_year == 2023
        assert statement.jurisdiction == 'ca'
        assert statement.district == 'District 10'
        assert statement.party == 'Republican'
    
    def test_entities_json_field(self):
        """Test storing entities as JSON."""
        entities = {
            'people': ['John Smith', 'Jane Doe'],
            'organizations': ['Department of Education'],
            'locations': ['Texas', 'Austin'],
            'dates': ['2023'],
            'money': ['$1 million'],
        }
        
        statement = MicroStatement.objects.create(
            actor="Actor",
            action="action",
            target="target",
            statement_text="test",
            entities=entities,
        )
        
        # Retrieve from DB and check
        retrieved = MicroStatement.objects.get(id=statement.id)
        assert retrieved.entities == entities
        assert retrieved.entities['people'] == ['John Smith', 'Jane Doe']
    
    def test_ordering(self):
        """Test that statements are ordered by extraction time."""
        stmt1 = MicroStatement.objects.create(
            actor="Actor1",
            action="action1",
            target="target1",
            statement_text="test1",
        )
        
        stmt2 = MicroStatement.objects.create(
            actor="Actor2",
            action="action2",
            target="target2",
            statement_text="test2",
        )
        
        # Most recent should be first
        statements = list(MicroStatement.objects.all())
        assert statements[0].id == stmt2.id
        assert statements[1].id == stmt1.id
    
    def test_confidence_score_bounds(self):
        """Test confidence score is properly stored."""
        statement = MicroStatement.objects.create(
            actor="Actor",
            action="action",
            target="target",
            statement_text="test",
            confidence_score=0.95,
        )
        
        assert statement.confidence_score == 0.95
        assert 0.0 <= statement.confidence_score <= 1.0
    
    def test_field_length_limits(self):
        """Test that long text is properly handled."""
        long_actor = "A" * 600  # Longer than 500 char limit
        
        statement = MicroStatement.objects.create(
            actor=long_actor[:500],  # Should be truncated
            action="action",
            target="target",
            statement_text="test",
        )
        
        assert len(statement.actor) == 500
