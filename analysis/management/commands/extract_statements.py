"""
Management command to extract micro-statements from bills using NLP.

Usage:
    python manage.py extract_statements --jurisdiction tx --limit 100
    python manage.py extract_statements --bill-id ocd-bill/...
    python manage.py extract_statements --session 2023
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openstates.data.models import Bill, LegislativeSession
from analysis.models import MicroStatement, BillTextAnalysis, AnalysisJob
from analysis.nlp_processor import get_processor
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Extract micro-statements from legislative bills using NLP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--jurisdiction',
            type=str,
            help='Jurisdiction code (e.g., tx, ca, ny)',
        )
        parser.add_argument(
            '--session',
            type=str,
            help='Legislative session identifier',
        )
        parser.add_argument(
            '--bill-id',
            type=str,
            help='Specific bill ID to process',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of bills to process',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of bills to process in each batch',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Reprocess bills that already have statements extracted',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        jurisdiction = options.get('jurisdiction')
        session = options.get('session')
        bill_id = options.get('bill_id')
        limit = options.get('limit')
        batch_size = options.get('batch_size')
        force = options.get('force')
        verbose = options.get('verbose')

        if verbose:
            logger.setLevel(logging.DEBUG)

        # Create analysis job for tracking
        job = AnalysisJob.objects.create(
            job_type='nlp',
            status='running',
            started_at=datetime.now(),
            parameters={
                'jurisdiction': jurisdiction,
                'session': session,
                'limit': limit,
            }
        )

        try:
            # Get bills to process
            bills = self._get_bills(jurisdiction, session, bill_id, limit, force)
            
            if not bills:
                self.stdout.write(self.style.WARNING('No bills found to process'))
                job.status = 'completed'
                job.completed_at = datetime.now()
                job.save()
                return

            self.stdout.write(self.style.SUCCESS(f'Found {len(bills)} bills to process'))
            
            job.total_items = len(bills)
            job.save()

            # Initialize NLP processor
            self.stdout.write('Initializing NLP models...')
            processor = get_processor()
            self.stdout.write(self.style.SUCCESS('NLP models loaded'))

            # Process bills in batches
            total_statements = 0
            processed_count = 0
            
            for i in range(0, len(bills), batch_size):
                batch = bills[i:i + batch_size]
                batch_statements = self._process_batch(batch, processor, verbose)
                total_statements += batch_statements
                processed_count += len(batch)
                
                # Update job progress
                job.processed_items = processed_count
                job.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed {processed_count}/{len(bills)} bills, '
                        f'extracted {total_statements} statements'
                    )
                )

            # Complete job
            job.status = 'completed'
            job.completed_at = datetime.now()
            job.results = {
                'bills_processed': processed_count,
                'statements_extracted': total_statements,
            }
            job.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCompleted! Processed {processed_count} bills and '
                    f'extracted {total_statements} micro-statements'
                )
            )

        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.now()
            job.save()
            raise CommandError(f'Processing failed: {e}')

    def _get_bills(self, jurisdiction, session, bill_id, limit, force):
        """Get bills to process based on filters."""
        if bill_id:
            # Process specific bill
            return [Bill.objects.get(id=bill_id)]

        # Build query
        query = Bill.objects.all()

        if jurisdiction:
            query = query.filter(
                legislative_session__jurisdiction_id=jurisdiction
            )

        if session:
            query = query.filter(
                legislative_session__identifier=session
            )

        # Exclude bills already processed unless force is set
        if not force:
            processed_bill_ids = MicroStatement.objects.values_list(
                'bill_id', flat=True
            ).distinct()
            query = query.exclude(id__in=processed_bill_ids)

        # Order by most recent and limit
        query = query.order_by('-created_at')[:limit]

        return list(query)

    def _process_batch(self, bills, processor, verbose):
        """Process a batch of bills and extract statements."""
        total_statements = 0

        for bill in bills:
            try:
                statements = self._process_bill(bill, processor, verbose)
                total_statements += statements
            except Exception as e:
                logger.error(f'Error processing bill {bill.id}: {e}')
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {bill.identifier}: {e}')
                    )

        return total_statements

    def _process_bill(self, bill, processor, verbose):
        """Process a single bill and extract statements."""
        if verbose:
            self.stdout.write(f'Processing bill: {bill.identifier}')

        # Get bill text
        bill_text = self._get_bill_text(bill)
        if not bill_text:
            if verbose:
                self.stdout.write(
                    self.style.WARNING(f'No text found for {bill.identifier}')
                )
            return 0

        # Prepare metadata
        metadata = self._get_bill_metadata(bill)

        # Extract statements
        statements = processor.extract_micro_statements(bill_text, metadata)

        if not statements:
            if verbose:
                self.stdout.write(
                    self.style.WARNING(
                        f'No statements extracted from {bill.identifier}'
                    )
                )
            return 0

        # Get or create BillTextAnalysis
        text_analysis, created = BillTextAnalysis.objects.get_or_create(
            bill=bill,
            defaults={'raw_text': bill_text[:10000]}  # Store first 10k chars
        )

        # Save statements to database
        with transaction.atomic():
            for stmt_data in statements:
                MicroStatement.objects.create(
                    bill=bill,
                    bill_text_analysis=text_analysis,
                    actor=stmt_data['actor'][:500],
                    action=stmt_data['action'][:500],
                    target=stmt_data['target'][:500],
                    statement_text=stmt_data['statement_text'],
                    original_text=stmt_data['original_text'],
                    statement_type=stmt_data['statement_type'],
                    sentiment=stmt_data['sentiment'],
                    sentiment_score=stmt_data['sentiment_score'],
                    session_year=stmt_data.get('session_year'),
                    jurisdiction=stmt_data.get('jurisdiction', '')[:10],
                    district=stmt_data.get('district', '')[:100],
                    party=stmt_data.get('party', '')[:50],
                    entities=stmt_data['entities'],
                    confidence_score=stmt_data['confidence_score'],
                    extraction_method=stmt_data['extraction_method'],
                )

        if verbose:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Extracted {len(statements)} statements from {bill.identifier}'
                )
            )

        return len(statements)

    def _get_bill_text(self, bill):
        """Extract text from bill."""
        # Try to get from abstracts field
        if hasattr(bill, 'abstracts') and bill.abstracts:
            abstracts = bill.abstracts.all()
            if abstracts:
                return ' '.join(a.abstract for a in abstracts if a.abstract)

        # Try to get from title and description
        text_parts = []
        if bill.title:
            text_parts.append(bill.title)
        
        # Try to get from versions
        if hasattr(bill, 'versions') and bill.versions:
            versions = bill.versions.all()[:1]  # Just get the first version
            for version in versions:
                if hasattr(version, 'note') and version.note:
                    text_parts.append(version.note)

        return ' '.join(text_parts) if text_parts else None

    def _get_bill_metadata(self, bill):
        """Extract metadata from bill for statement attribution."""
        metadata = {}

        # Get session year
        if bill.legislative_session:
            try:
                # Try to parse year from identifier
                year_str = ''.join(c for c in bill.legislative_session.identifier if c.isdigit())
                if year_str:
                    metadata['session_year'] = int(year_str[:4])
            except (ValueError, AttributeError):
                pass

            # Get jurisdiction
            if bill.legislative_session.jurisdiction_id:
                metadata['jurisdiction'] = bill.legislative_session.jurisdiction_id

        # Get sponsor party if available
        if hasattr(bill, 'sponsorships') and bill.sponsorships:
            sponsorships = bill.sponsorships.all()[:1]
            for sponsorship in sponsorships:
                if sponsorship.person and hasattr(sponsorship.person, 'current_party'):
                    party = sponsorship.person.current_party
                    if party:
                        metadata['party'] = party.name if hasattr(party, 'name') else str(party)

        return metadata
