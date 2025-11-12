# Analysis Dashboard

The Analysis Dashboard provides comprehensive tools for bulk data analysis, NLP processing, and member profile aggregation for OpenStates data.

## Features

### 1. Bulk Data Ingestion
- CLI tool for downloading all OpenStates data to a target database
- Supports filtering by jurisdiction and data type
- Connection string-based configuration
- Progress tracking and logging

### 2. Analysis Dashboard Web Interface
- Menu-driven navigation
- Data explorer for browsing jurisdictions and sessions
- Real-time job status monitoring
- Legislator profile aggregation

### 3. NLP Analysis
- **Micro-statement extraction**: Extract Actor + Action + Target triples from bills
- **BERT-based sentiment analysis**: Classify statements as positive/negative/neutral
- **spaCy entity extraction**: Extract people, organizations, locations from text
- **Sentence transformer embeddings**: Generate semantic embeddings for similarity
- **Binning & comparison**: Analyze across years, jurisdictions, parties, districts
- See [NLP_GUIDE.md](NLP_GUIDE.md) for detailed documentation

### 4. Member Profile Viewer
- Aggregated legislator data
- Voting record analysis
- Bill sponsorship tracking
- Social media comparison (when available)

## Quick Start

### Installation

The analysis app is automatically included when you install the openstates.org project.

### Using the Bulk Data Ingestion CLI

List available jurisdictions:
```bash
python manage.py bulk_ingest --list-jurisdictions
```

Ingest all data for specific jurisdictions:
```bash
python manage.py bulk_ingest --jurisdictions "tx,ca,ny" --data-types "all"
```

Ingest only bills and votes:
```bash
python manage.py bulk_ingest --jurisdictions "tx" --data-types "bills,votes"
```

Use a custom database connection:
```bash
python manage.py bulk_ingest \
    --connection-string "postgresql://user:pass@host:5432/dbname" \
    --jurisdictions "tx"
```

Dry run to see what would be ingested:
```bash
python manage.py bulk_ingest --jurisdictions "tx" --dry-run
```

### Accessing the Dashboard

1. Start the development server:
```bash
docker-compose up
```

2. Navigate to: `http://localhost:8000/analysis/`

### Running Analysis Jobs

1. Go to the dashboard: `http://localhost:8000/analysis/`
2. Click "Run Analysis"
3. Select analysis type and parameters
4. Submit the job
5. Monitor progress in the jobs list

## Database Models

### AnalysisJob
Tracks analysis job execution, status, and results.

### BillTextAnalysis
Stores NLP analysis results for bill text including:
- Sentiment scores
- Extracted topics
- Named entities
- Text embeddings
- Summaries

### LegislatorProfile
Aggregated legislator data including:
- Voting statistics
- Bill sponsorship stats
- Primary topics
- Voting patterns
- Social media analysis

### VoteAnalysis
Vote-level analysis including:
- Party line scores
- Bipartisan indicators
- Topic relationships

### DataIngestionLog
Logs bulk data ingestion operations with statistics.

## Architecture

The analysis system is built as a Django app that integrates with the existing OpenStates infrastructure:

- **Models**: PostgreSQL database models for storing analysis results
- **Views**: Django views for web interface
- **Management Commands**: CLI tools for bulk operations
- **Templates**: HTML templates using Foundation CSS (matching existing UI)
- **API Endpoints**: JSON endpoints for real-time updates

## Docker Support

The analysis app works with the existing Docker setup. No additional configuration needed for local development.

For production deployment with external database:

```yaml
# docker-compose.override.yml
services:
  django:
    environment:
      - DATABASE_URL=postgresql://user:pass@external-host:5432/dbname
```

## NLP Integration

NLP capabilities are now built into the analysis app.

### Setup

Install dependencies:
```bash
poetry install
python -m spacy download en_core_web_sm
```

### Extract Micro-Statements

```bash
# Extract from Texas bills
python manage.py extract_statements --jurisdiction tx --limit 100

# Extract with session filter
python manage.py extract_statements --jurisdiction ca --session 2023

# View results
# Navigate to: http://localhost:8000/analysis/micro-statements/
```

See [NLP_GUIDE.md](NLP_GUIDE.md) for complete documentation.

## API Endpoints

- `GET /analysis/api/stats/` - Dashboard statistics
- `GET /analysis/api/job-status/<job_id>/` - Job status

## Development

### Running Tests

```bash
pytest analysis/tests/
```

### Creating New Analysis Types

1. Add job type to `AnalysisJob.JOB_TYPES`
2. Implement worker in `analysis/workers/`
3. Add form fields in `run_analysis.html`
4. Update views to handle new parameters

### Adding New Models

```bash
python manage.py makemigrations analysis
python manage.py migrate analysis
```

## Contributing

Follow the standard OpenStates contribution guidelines:
1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## Security Considerations

- Database credentials are never stored in logs
- Only connection metadata (type, host, database name) is logged
- User authentication required for running analysis jobs
- Input validation on all form submissions

## Performance Tips

- Use `--dry-run` first to estimate data volume
- Start with single jurisdictions for testing
- Monitor job progress via the dashboard
- Consider batch processing for large datasets

## Troubleshooting

### Job Fails Immediately
- Check database connectivity
- Verify jurisdiction codes
- Review error message in job detail page

### Slow Performance
- Index database tables appropriately
- Use smaller batch sizes
- Process jurisdictions separately

### Missing Data
- Verify data exists in source database
- Check filter parameters
- Review ingestion logs

## License

Same as openstates.org - see LICENSE file in repository root.
