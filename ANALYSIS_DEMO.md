# Analysis Dashboard Demo Guide

This guide demonstrates how to use the new Analysis Dashboard and Bulk Data Ingestion system.

## Overview

The Analysis Dashboard provides:
1. **Bulk Data Ingestion CLI** - Download all OpenStates data to any database
2. **Web Dashboard** - Menu-driven interface for exploring data and running analyses
3. **Legislator Profiles** - Aggregated member data with voting records and bill sponsorships
4. **Job Management** - Submit and monitor analysis jobs
5. **Data Explorer** - Navigate jurisdictions, sessions, and data types

## Setup

### 1. Initial Setup

```bash
# Navigate to project directory
cd /home/runner/work/openstates.org/openstates.org

# Create database migrations
python manage.py makemigrations analysis

# Apply migrations
python manage.py migrate analysis

# Start development server
python manage.py runserver
```

Or with Docker:

```bash
# Build and start containers
docker-compose up --build

# In another terminal, run migrations
docker-compose exec django python manage.py makemigrations analysis
docker-compose exec django python manage.py migrate analysis
```

### 2. Access the Dashboard

Open your browser to: `http://localhost:8000/analysis/`

## CLI Examples

### List Available Jurisdictions

```bash
python manage.py bulk_ingest --list-jurisdictions
```

Output:
```
=== Available Jurisdictions ===

  tx    - Texas                          (25 sessions)
  ca    - California                     (30 sessions)
  ny    - New York                       (28 sessions)
  ...
```

### Dry Run - See What Would Be Ingested

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx" \
    --data-types "bills,votes" \
    --dry-run \
    --verbose
```

### Ingest Data for Specific Jurisdictions

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx,ca,ny" \
    --data-types "all"
```

### Ingest to Custom Database

```bash
python manage.py bulk_ingest \
    --connection-string "postgresql://user:password@cloudcurio.cc:5432/openstates" \
    --jurisdictions "tx" \
    --data-types "bills,votes,people"
```

### Ingest Only Bills

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx" \
    --data-types "bills"
```

## Web Dashboard Usage

### 1. Main Dashboard

Navigate to: `http://localhost:8000/analysis/`

Features:
- **Statistics Cards**: Live counts of analyses, profiles, and jobs
- **Recent Jobs**: Monitor analysis job status
- **Recent Ingestions**: View bulk data import history
- **Quick Links**: Access to other tools and APIs

### 2. Data Explorer

Navigate to: `http://localhost:8000/analysis/explorer/`

Steps:
1. Select a jurisdiction from dropdown
2. Select a legislative session
3. View data summary and statistics
4. Access bulk download or run analysis

### 3. Search Legislators

Navigate to: `http://localhost:8000/analysis/legislators/search/`

Steps:
1. Enter legislator name in search box
2. Optionally filter by jurisdiction
3. Click "Search"
4. Click "View Profile" on any result

### 4. Legislator Profile Page

Navigate to: `http://localhost:8000/analysis/legislator/<person-id>/`

Features displayed:
- **Profile Header**: Name, party, role, photo
- **Voting Record**: Total votes broken down by yes/no/abstain
- **Sponsored Legislation**: Bills with primary/co-sponsor designation
- **Primary Topics**: Main legislative focus areas
- **Recent Votes**: Last 20 votes with bill and motion details
- **Recent Bills**: Last 20 sponsored bills with analysis status
- **Analysis Insights**: Voting-social media discrepancy (when available)

Example: Wikipedia-style aggregated view of a legislator with:
- Vote summary charts
- Bill sponsorship statistics
- Topic clouds
- Comparison with social media (future)
- NLP findings on voting patterns (future)

### 5. Submit Analysis Job

Navigate to: `http://localhost:8000/analysis/run-analysis/`

Steps:
1. Select analysis type:
   - NLP Analysis
   - Embeddings Generation
   - Sentiment Analysis
   - Comparison Analysis
   - Bulk Data Import
2. Optionally select jurisdiction and session
3. Click "Submit Job"
4. View job status in real-time

### 6. Monitor Jobs

Navigate to: `http://localhost:8000/analysis/jobs/`

Features:
- Filter by job type
- Filter by status (pending, running, completed, failed)
- View progress bars
- Click to see detailed job information

### 7. View Ingestion Logs

Navigate to: `http://localhost:8000/analysis/ingestion-logs/`

See history of all bulk data ingestion operations with:
- Database connection info
- Jurisdictions imported
- Status and timestamps
- Statistics (bills, votes, people counts)

## Integration with Existing Tools

### 1. GraphQL API

The dashboard integrates with the existing GraphQL API at `/graphql`

Example query for legislator data:
```graphql
query {
  person(id: "ocd-person/...") {
    name
    party {
      name
    }
    currentMemberships {
      organization {
        name
      }
    }
  }
}
```

### 2. Bulk Data Downloads

Link to existing bulk data downloads: `/data/`

### 3. Data Quality Dashboard

Link to existing quality dashboard: `/dashboard/`

## Analysis Workflows

### Workflow 1: Analyze a Specific State

1. **Ingest Data**:
   ```bash
   python manage.py bulk_ingest --jurisdictions "tx" --data-types "all"
   ```

2. **View in Explorer**: Navigate to Data Explorer, select Texas

3. **Run Analysis**: Submit NLP analysis job for Texas bills

4. **Monitor Progress**: Check Jobs page for status

5. **View Results**: Access analyzed bills in legislator profiles

### Workflow 2: Compare Legislators

1. **Search for First Legislator**: Use Search page

2. **View Profile**: Note voting patterns and topics

3. **Search for Second Legislator**: Compare results

4. **Run Comparison Analysis**: Submit comparison job (future feature)

### Workflow 3: Bulk Analysis

1. **List All Jurisdictions**:
   ```bash
   python manage.py bulk_ingest --list-jurisdictions
   ```

2. **Ingest Multiple States**:
   ```bash
   python manage.py bulk_ingest --jurisdictions "tx,ca,ny,fl,oh"
   ```

3. **Submit Batch Jobs**: Run NLP analysis for each jurisdiction

4. **Aggregate Results**: View results across all jurisdictions

## API Usage

### Get Dashboard Stats

```bash
curl http://localhost:8000/analysis/api/stats/
```

Response:
```json
{
  "total_bills": 150000,
  "total_votes": 75000,
  "total_people": 7500,
  "total_analyses": 1200,
  "total_profiles": 450,
  "total_jobs": 25,
  "pending_jobs": 2,
  "running_jobs": 1
}
```

### Check Job Status

```bash
curl http://localhost:8000/analysis/api/job-status/1/
```

Response:
```json
{
  "id": 1,
  "job_type": "nlp",
  "status": "running",
  "progress": 45.5,
  "processed_items": 455,
  "total_items": 1000,
  "created_at": "2025-11-10T10:00:00Z",
  "error_message": ""
}
```

## Future Enhancements

### NLP Analysis (Ready to Implement)

Install dependencies:
```bash
poetry add spacy transformers sentence-transformers
python -m spacy download en_core_web_sm
```

Then implement workers in `analysis/workers/nlp_worker.py`:
- BERT sentiment analysis
- spaCy entity extraction
- Sentence transformer embeddings
- Topic modeling with LDA
- Text summarization with NLG

### Social Media Integration

- Twitter API integration for legislator tweets
- Compare voting record with social media statements
- Identify discrepancies using NLP
- Display findings on profile pages

### Advanced Visualizations

- D3.js voting pattern charts
- Network graphs of bill co-sponsorships
- Topic distribution visualizations
- Timeline of legislative activity

### Batch Processing System

- Celery task queue for long-running jobs
- Redis for job state management
- Progress notifications via WebSockets
- Email notifications on job completion

## Troubleshooting

### Issue: ImportError for analysis app

**Solution**: Make sure migrations are applied:
```bash
python manage.py migrate analysis
```

### Issue: Database connection error

**Solution**: Check DATABASE_URL environment variable:
```bash
echo $DATABASE_URL
```

### Issue: Templates not found

**Solution**: Verify templates directory exists:
```bash
ls -la templates/analysis/
```

### Issue: Job status not updating

**Solution**: Refresh the page or check browser console for JavaScript errors

## Performance Considerations

- **Large Datasets**: Use pagination and filtering
- **Concurrent Jobs**: Limit to 3-5 simultaneous jobs
- **Database Indexes**: Created automatically via migrations
- **Caching**: Consider Redis for frequently accessed data

## Security Notes

- Database credentials never stored in logs
- User authentication required for job submission
- CSRF protection on all forms
- Input validation on all parameters
- SQL injection prevention via Django ORM

## Support

For issues or questions:
1. Check the README: `analysis/README.md`
2. Review existing issues on GitHub
3. Submit new issue with reproduction steps
4. Contact maintainers via Discussions

## License

Same as openstates.org - see LICENSE file in repository root.
