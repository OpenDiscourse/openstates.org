"""
Bulk data ingestion command.

Downloads all OpenStates data to a target database via connection string.
Supports filtering by jurisdiction and data type.
"""
import sys
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from openstates.data.models import (
    Jurisdiction,
    LegislativeSession,
    Bill,
    Person,
    Organization,
    VoteEvent,
)
from ...models import DataIngestionLog

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Bulk data ingestion tool for OpenStates data.
    
    Usage:
        python manage.py bulk_ingest --connection-string "postgresql://user:pass@host:5432/dbname"
        python manage.py bulk_ingest --jurisdictions "tx,ca,ny"
        python manage.py bulk_ingest --data-types "bills,votes"
        python manage.py bulk_ingest --list-jurisdictions
    """
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--connection-string',
            type=str,
            help='Database connection string (postgresql://user:pass@host:5432/dbname)',
        )
        parser.add_argument(
            '--jurisdictions',
            type=str,
            help='Comma-separated list of jurisdiction abbreviations (e.g., tx,ca,ny). Default: all',
        )
        parser.add_argument(
            '--data-types',
            type=str,
            default='all',
            help='Comma-separated list of data types: bills,votes,people,organizations. Default: all',
        )
        parser.add_argument(
            '--list-jurisdictions',
            action='store_true',
            help='List available jurisdictions and exit',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be ingested without actually doing it',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
    
    def handle(self, *args, **options):
        # Set up logging
        if options['verbose']:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        # List jurisdictions if requested
        if options['list_jurisdictions']:
            self.list_jurisdictions()
            return
        
        # Validate connection string
        conn_string = options.get('connection_string')
        if conn_string:
            self.validate_connection_string(conn_string)
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No connection string provided. Using current database connection.'
                )
            )
        
        # Parse options
        jurisdictions = self.parse_jurisdictions(options.get('jurisdictions'))
        data_types = self.parse_data_types(options.get('data_types', 'all'))
        dry_run = options['dry_run']
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\n=== Bulk Data Ingestion ==='))
        self.stdout.write(f"Jurisdictions: {', '.join(jurisdictions) if jurisdictions else 'ALL'}")
        self.stdout.write(f"Data types: {', '.join(data_types)}")
        self.stdout.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No data will be modified'))
        
        # Create ingestion log
        log_entry = None
        if not dry_run:
            db_info = self.parse_database_info(conn_string)
            log_entry = DataIngestionLog.objects.create(
                database_type=db_info['type'],
                database_host=db_info['host'],
                database_name=db_info['name'],
                jurisdictions=jurisdictions or [],
                status='running',
            )
        
        try:
            # Execute ingestion
            stats = self.ingest_data(jurisdictions, data_types, dry_run)
            
            # Update log
            if log_entry:
                log_entry.status = 'completed'
                log_entry.completed_at = datetime.now(timezone.utc)
                log_entry.total_bills = stats.get('bills', 0)
                log_entry.total_votes = stats.get('votes', 0)
                log_entry.total_people = stats.get('people', 0)
                log_entry.save()
            
            # Display results
            self.display_results(stats)
            
        except Exception as e:
            if log_entry:
                log_entry.status = 'failed'
                log_entry.completed_at = datetime.now(timezone.utc)
                log_entry.error_message = str(e)
                log_entry.save()
            
            self.stdout.write(self.style.ERROR(f'\nIngestion failed: {str(e)}'))
            raise
    
    def list_jurisdictions(self):
        """List all available jurisdictions."""
        self.stdout.write(self.style.SUCCESS('\n=== Available Jurisdictions ===\n'))
        
        jurisdictions = Jurisdiction.objects.all().order_by('name')
        for jur in jurisdictions:
            # Get abbreviation from classification
            abbr = jur.classification.split(':')[-1] if ':' in jur.classification else 'N/A'
            sessions_count = LegislativeSession.objects.filter(jurisdiction=jur).count()
            self.stdout.write(f"  {abbr:5} - {jur.name:30} ({sessions_count} sessions)")
        
        self.stdout.write('')
    
    def validate_connection_string(self, conn_string):
        """Validate the database connection string format."""
        try:
            parsed = urlparse(conn_string)
            if not parsed.scheme in ('postgresql', 'postgres', 'mysql'):
                raise ValueError(f"Unsupported database type: {parsed.scheme}")
            if not parsed.hostname:
                raise ValueError("Missing hostname in connection string")
        except Exception as e:
            raise CommandError(f"Invalid connection string: {str(e)}")
    
    def parse_database_info(self, conn_string):
        """Parse database connection info."""
        if not conn_string:
            # Use current connection
            conn_settings = connection.settings_dict
            return {
                'type': conn_settings.get('ENGINE', 'unknown').split('.')[-1],
                'host': conn_settings.get('HOST', 'localhost'),
                'name': conn_settings.get('NAME', 'unknown'),
            }
        
        parsed = urlparse(conn_string)
        return {
            'type': parsed.scheme,
            'host': parsed.hostname or 'localhost',
            'name': parsed.path.lstrip('/') if parsed.path else 'unknown',
        }
    
    def parse_jurisdictions(self, jurisdictions_str):
        """Parse jurisdiction list from string."""
        if not jurisdictions_str:
            return []
        return [j.strip().lower() for j in jurisdictions_str.split(',')]
    
    def parse_data_types(self, data_types_str):
        """Parse data types list from string."""
        if data_types_str == 'all':
            return ['bills', 'votes', 'people', 'organizations']
        return [dt.strip().lower() for dt in data_types_str.split(',')]
    
    def ingest_data(self, jurisdictions, data_types, dry_run):
        """Perform the actual data ingestion."""
        stats = {}
        
        # Filter by jurisdictions if specified
        if jurisdictions:
            jur_filter = Jurisdiction.objects.filter(
                classification__icontains=jurisdictions[0]
            )
            for jur_abbr in jurisdictions[1:]:
                jur_filter |= Jurisdiction.objects.filter(
                    classification__icontains=jur_abbr
                )
        else:
            jur_filter = Jurisdiction.objects.all()
        
        # Ingest each data type
        if 'bills' in data_types:
            stats['bills'] = self.ingest_bills(jur_filter, dry_run)
        
        if 'votes' in data_types:
            stats['votes'] = self.ingest_votes(jur_filter, dry_run)
        
        if 'people' in data_types:
            stats['people'] = self.ingest_people(jur_filter, dry_run)
        
        if 'organizations' in data_types:
            stats['organizations'] = self.ingest_organizations(jur_filter, dry_run)
        
        return stats
    
    def ingest_bills(self, jurisdictions, dry_run):
        """Ingest bills data."""
        self.stdout.write('\nIngesting bills...')
        
        # Get sessions for the specified jurisdictions
        sessions = LegislativeSession.objects.filter(
            jurisdiction__in=jurisdictions
        )
        
        total_bills = 0
        for session in sessions:
            bills = Bill.objects.filter(legislative_session=session)
            count = bills.count()
            total_bills += count
            
            if count > 0:
                self.stdout.write(
                    f"  {session.jurisdiction.name} - {session.identifier}: {count} bills"
                )
        
        return total_bills
    
    def ingest_votes(self, jurisdictions, dry_run):
        """Ingest votes data."""
        self.stdout.write('\nIngesting votes...')
        
        sessions = LegislativeSession.objects.filter(
            jurisdiction__in=jurisdictions
        )
        
        total_votes = 0
        for session in sessions:
            votes = VoteEvent.objects.filter(legislative_session=session)
            count = votes.count()
            total_votes += count
            
            if count > 0:
                self.stdout.write(
                    f"  {session.jurisdiction.name} - {session.identifier}: {count} votes"
                )
        
        return total_votes
    
    def ingest_people(self, jurisdictions, dry_run):
        """Ingest people data."""
        self.stdout.write('\nIngesting people...')
        
        total_people = 0
        for jurisdiction in jurisdictions:
            people = Person.objects.filter(
                memberships__organization__jurisdiction=jurisdiction
            ).distinct()
            count = people.count()
            total_people += count
            
            if count > 0:
                self.stdout.write(f"  {jurisdiction.name}: {count} people")
        
        return total_people
    
    def ingest_organizations(self, jurisdictions, dry_run):
        """Ingest organizations data."""
        self.stdout.write('\nIngesting organizations...')
        
        total_orgs = 0
        for jurisdiction in jurisdictions:
            orgs = Organization.objects.filter(jurisdiction=jurisdiction)
            count = orgs.count()
            total_orgs += count
            
            if count > 0:
                self.stdout.write(f"  {jurisdiction.name}: {count} organizations")
        
        return total_orgs
    
    def display_results(self, stats):
        """Display ingestion results."""
        self.stdout.write(self.style.SUCCESS('\n=== Ingestion Complete ==='))
        self.stdout.write(f"Total bills: {stats.get('bills', 0)}")
        self.stdout.write(f"Total votes: {stats.get('votes', 0)}")
        self.stdout.write(f"Total people: {stats.get('people', 0)}")
        self.stdout.write(f"Total organizations: {stats.get('organizations', 0)}")
        self.stdout.write('')
