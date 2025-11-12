"""
Models for storing analysis results and batch job information.
"""
from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from openstates.data.models import Person, Bill, VoteEvent, LegislativeSession


class AnalysisJob(models.Model):
    """Track bulk analysis jobs and their status."""
    
    JOB_TYPES = [
        ('nlp', 'NLP Analysis'),
        ('embeddings', 'Embeddings Generation'),
        ('sentiment', 'Sentiment Analysis'),
        ('comparison', 'Comparison Analysis'),
        ('bulk_import', 'Bulk Data Import'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.AutoField(primary_key=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    parameters = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Progress tracking
    total_items = models.IntegerField(default=0)
    processed_items = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['job_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_job_type_display()} - {self.status} ({self.created_at})"


class BillTextAnalysis(models.Model):
    """Store NLP analysis results for bill text."""
    
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE, related_name='text_analysis')
    analyzed_at = models.DateTimeField(auto_now=True)
    
    # Text content
    raw_text = models.TextField(blank=True)
    
    # NLP results
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=20, blank=True)
    
    # Key topics/subjects extracted
    extracted_topics = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True
    )
    
    # Named entities
    entities = models.JSONField(default=dict, blank=True)
    
    # Embeddings (stored as JSON array)
    embeddings = models.JSONField(default=list, blank=True)
    
    # Summary
    summary = models.TextField(blank=True)
    
    # Metadata
    analysis_metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name_plural = "Bill text analyses"
        indexes = [
            models.Index(fields=['sentiment_score']),
        ]
    
    def __str__(self):
        return f"Analysis for {self.bill.identifier}"


class LegislatorProfile(models.Model):
    """Aggregated profile data for legislators with analysis results."""
    
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='analysis_profile')
    updated_at = models.DateTimeField(auto_now=True)
    
    # Voting statistics
    total_votes = models.IntegerField(default=0)
    yes_votes = models.IntegerField(default=0)
    no_votes = models.IntegerField(default=0)
    abstain_votes = models.IntegerField(default=0)
    other_votes = models.IntegerField(default=0)
    
    # Bill sponsorship statistics
    total_sponsored_bills = models.IntegerField(default=0)
    primary_sponsored_bills = models.IntegerField(default=0)
    co_sponsored_bills = models.IntegerField(default=0)
    
    # Topic analysis
    primary_topics = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    # Voting patterns
    voting_alignment = models.JSONField(default=dict, blank=True)
    
    # Social media analysis (if available)
    social_media_sentiment = models.FloatField(null=True, blank=True)
    social_media_topics = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    # Discrepancy indicators
    voting_social_discrepancy = models.FloatField(null=True, blank=True)
    
    # Recent activity summary
    recent_votes_summary = models.JSONField(default=dict, blank=True)
    recent_bills_summary = models.JSONField(default=dict, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Profile for {self.person.name}"


class VoteAnalysis(models.Model):
    """Analysis of voting patterns and alignments."""
    
    vote_event = models.OneToOneField(VoteEvent, on_delete=models.CASCADE, related_name='vote_analysis')
    analyzed_at = models.DateTimeField(auto_now=True)
    
    # Voting alignment scores
    party_line_score = models.FloatField(null=True, blank=True)
    bipartisan_score = models.FloatField(null=True, blank=True)
    
    # Contextual analysis
    related_topics = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    # Bill context if available
    bill_sentiment = models.FloatField(null=True, blank=True)
    
    # Additional metadata
    analysis_metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name_plural = "Vote analyses"
    
    def __str__(self):
        return f"Vote Analysis for {self.vote_event.identifier}"


class DataIngestionLog(models.Model):
    """Log entries for bulk data ingestion operations."""
    
    id = models.AutoField(primary_key=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Connection info (no credentials stored)
    database_type = models.CharField(max_length=50)
    database_host = models.CharField(max_length=255)
    database_name = models.CharField(max_length=255)
    
    # What was imported
    jurisdictions = ArrayField(
        models.CharField(max_length=10),
        default=list,
        blank=True
    )
    
    # Stats
    total_bills = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    total_people = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='running'
    )
    
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Ingestion {self.id} - {self.status} ({self.started_at})"


class MicroStatement(models.Model):
    """
    Store extracted micro-statements from bills following the pattern:
    Actor (politicians/legislators) + Action (verb) + Target (voters/citizens)
    
    Enables binning and comparison across years, districts, parties, and bills.
    """
    
    STATEMENT_TYPES = [
        ('action', 'Legislative Action'),
        ('position', 'Political Position'),
        ('impact', 'Impact Statement'),
    ]
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('mixed', 'Mixed'),
    ]
    
    id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='micro_statements')
    bill_text_analysis = models.ForeignKey(
        BillTextAnalysis, 
        on_delete=models.CASCADE, 
        related_name='micro_statements',
        null=True,
        blank=True
    )
    
    # Extracted statement components
    actor = models.CharField(max_length=500, help_text="Who is taking action (e.g., legislators, politicians)")
    action = models.CharField(max_length=500, help_text="What action is being taken (verb phrase)")
    target = models.CharField(max_length=500, help_text="Who is affected (e.g., voters, citizens, groups)")
    
    # Full statement text
    statement_text = models.TextField(help_text="Complete extracted statement")
    original_text = models.TextField(help_text="Original text from bill", blank=True)
    
    # Classification
    statement_type = models.CharField(max_length=20, choices=STATEMENT_TYPES, default='action')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    sentiment_score = models.FloatField(null=True, blank=True, help_text="Sentiment score from -1 (negative) to 1 (positive)")
    
    # Metadata for binning and comparison
    session_year = models.IntegerField(null=True, blank=True, help_text="Legislative session year")
    jurisdiction = models.CharField(max_length=10, blank=True, help_text="State/jurisdiction code")
    district = models.CharField(max_length=100, blank=True, help_text="Legislative district")
    party = models.CharField(max_length=50, blank=True, help_text="Political party")
    
    # Named entities extracted
    entities = models.JSONField(default=dict, blank=True, help_text="Named entities (people, orgs, locations)")
    
    # Extraction metadata
    confidence_score = models.FloatField(null=True, blank=True, help_text="Confidence in extraction quality")
    extraction_method = models.CharField(max_length=100, blank=True, help_text="Method used for extraction")
    extracted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['bill']),
            models.Index(fields=['session_year']),
            models.Index(fields=['jurisdiction']),
            models.Index(fields=['district']),
            models.Index(fields=['party']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['statement_type']),
            models.Index(fields=['session_year', 'jurisdiction']),
            models.Index(fields=['session_year', 'party']),
        ]
        ordering = ['-extracted_at']
    
    def __str__(self):
        return f"{self.actor} {self.action} {self.target}"
