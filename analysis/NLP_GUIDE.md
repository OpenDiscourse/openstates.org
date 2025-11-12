# NLP Micro-Statement Extraction Guide

This guide explains how to use the NLP-based micro-statement extraction system to analyze legislative bills.

## Overview

The micro-statement extraction system uses Natural Language Processing (NLP) to:

1. **Extract Structured Statements**: Break down bill text into micro-statements following the pattern:
   - **Actor** (who): Politicians, legislators, government bodies
   - **Action** (what): Verbs describing legislative actions
   - **Target** (whom): Citizens, voters, affected groups

2. **Analyze Sentiment**: Determine if statements are positive, negative, or neutral

3. **Enable Comparison**: Store statements with metadata for cross-sectional analysis:
   - By year (temporal trends)
   - By jurisdiction (state comparisons)
   - By party (partisan analysis)
   - By district (geographical analysis)

## Installation

### 1. Install Dependencies

The required NLP libraries are already in `pyproject.toml`:

```bash
poetry install
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Run Migrations

```bash
python manage.py migrate analysis
```

## Usage

### Command Line Interface

#### Extract Statements from Bills

**Basic Usage:**
```bash
python manage.py extract_statements --jurisdiction tx --limit 100
```

**With Specific Session:**
```bash
python manage.py extract_statements --jurisdiction ca --session 2023 --limit 50
```

**Process Single Bill:**
```bash
python manage.py extract_statements --bill-id ocd-bill/...
```

**Batch Processing:**
```bash
python manage.py extract_statements \
    --jurisdiction tx \
    --limit 1000 \
    --batch-size 20 \
    --verbose
```

**Reprocess Bills:**
```bash
python manage.py extract_statements \
    --jurisdiction ny \
    --force \
    --verbose
```

#### Command Options

- `--jurisdiction`: State/jurisdiction code (e.g., tx, ca, ny)
- `--session`: Legislative session identifier
- `--bill-id`: Process a specific bill
- `--limit`: Maximum number of bills to process (default: 100)
- `--batch-size`: Bills per batch (default: 10)
- `--force`: Reprocess bills already analyzed
- `--verbose`: Enable detailed output

### Web Interface

#### 1. Micro-Statements Explorer

Navigate to: `http://localhost:8000/analysis/micro-statements/`

**Features:**
- Filter by year, jurisdiction, party, district
- View statistics and aggregations
- See sentiment distribution
- Export results

**Filter Examples:**
- Find all statements from 2023 in Texas
- Compare Democratic vs Republican statements
- Analyze sentiment trends over years
- View district-specific statements

#### 2. Statement Detail View

Click any statement to see:
- Full extracted statement
- Original bill text
- Named entities (people, organizations, locations)
- Confidence score
- Related bill information
- Similar statements

#### 3. Comparison Dashboard

Navigate to comparison views for:
- Year-over-year trends
- Party comparisons
- Jurisdiction comparisons
- Statement type distributions

### API Endpoints

#### Search Statements

```bash
curl "http://localhost:8000/analysis/api/micro-statements/search/?q=education&limit=20"
```

Response:
```json
{
  "query": "education",
  "count": 15,
  "results": [
    {
      "id": 1,
      "actor": "The legislature",
      "action": "shall provide",
      "target": "funding to schools",
      "statement_text": "The legislature shall provide funding to schools",
      "sentiment": "positive",
      "sentiment_score": 0.85,
      "bill_id": "HB123",
      "jurisdiction": "tx",
      "session_year": 2023,
      "party": "Democratic",
      "confidence_score": 0.92
    }
  ]
}
```

#### Compare Across Dimensions

```bash
# Compare by year and party
curl "http://localhost:8000/analysis/api/micro-statements/comparison/?type=year_party"

# Compare by jurisdiction and year
curl "http://localhost:8000/analysis/api/micro-statements/comparison/?type=jurisdiction_year"

# Compare statement types
curl "http://localhost:8000/analysis/api/micro-statements/comparison/?type=statement_type"
```

## Understanding the Data

### Statement Structure

Each micro-statement has:

```python
{
    'actor': "The legislature",        # Who is taking action
    'action': "shall provide",         # What action is taken
    'target': "funding to schools",    # Who/what is affected
    'sentiment': "positive",           # Sentiment classification
    'sentiment_score': 0.85,          # Score from -1 to 1
    'confidence_score': 0.92,         # Extraction quality
    'entities': {                      # Named entities
        'people': [...],
        'organizations': [...],
        'locations': [...],
    }
}
```

### Statement Types

1. **Legislative Action**: Actions taken by government
   - Example: "The senate shall establish a committee"
   
2. **Political Position**: Stated positions or beliefs
   - Example: "The representative supports healthcare reform"
   
3. **Impact Statement**: Effects on people/groups
   - Example: "The law will benefit small businesses"

### Sentiment Classification

- **Positive** (score > 0.3): Beneficial, supportive statements
- **Negative** (score < -0.3): Restrictive, opposing statements
- **Neutral** (-0.3 to 0.3): Factual, neutral statements
- **Mixed**: Statements with both positive and negative aspects

### Confidence Score

Indicates extraction quality (0.0 to 1.0):
- **0.9-1.0**: High confidence - clear statement structure
- **0.7-0.9**: Medium confidence - acceptable extraction
- **Below 0.7**: Low confidence - may need review

## Analysis Examples

### Example 1: Temporal Analysis

Compare how healthcare statements changed over years:

```python
from analysis.models import MicroStatement
from django.db.models import Count, Avg

# Get healthcare statements by year
statements = MicroStatement.objects.filter(
    Q(actor__icontains='health') | 
    Q(target__icontains='health')
).values('session_year').annotate(
    count=Count('id'),
    avg_sentiment=Avg('sentiment_score')
).order_by('session_year')
```

### Example 2: Party Comparison

Compare Democratic vs Republican statements:

```python
# Democratic statements
dem_statements = MicroStatement.objects.filter(
    party__icontains='Democratic'
).aggregate(
    total=Count('id'),
    avg_sentiment=Avg('sentiment_score')
)

# Republican statements
rep_statements = MicroStatement.objects.filter(
    party__icontains='Republican'
).aggregate(
    total=Count('id'),
    avg_sentiment=Avg('sentiment_score')
)
```

### Example 3: Topic Analysis

Find statements about specific topics:

```python
# Education-related statements
education_statements = MicroStatement.objects.filter(
    Q(target__icontains='school') |
    Q(target__icontains='student') |
    Q(target__icontains='education')
).values('jurisdiction', 'party').annotate(
    count=Count('id')
).order_by('-count')
```

### Example 4: Geographic Analysis

Compare jurisdictions:

```python
# By jurisdiction
by_state = MicroStatement.objects.values(
    'jurisdiction', 'sentiment'
).annotate(
    count=Count('id')
).order_by('jurisdiction', 'sentiment')
```

## Advanced Features

### Custom Extraction

You can use the NLP processor directly:

```python
from analysis.nlp_processor import get_processor

processor = get_processor()

# Extract statements from custom text
bill_text = "The legislature shall provide funding to public schools..."
metadata = {
    'session_year': 2023,
    'jurisdiction': 'tx',
    'party': 'Democratic'
}

statements = processor.extract_micro_statements(bill_text, metadata)
```

### Sentiment Analysis

Analyze sentiment of arbitrary text:

```python
from analysis.nlp_processor import get_processor

processor = get_processor()
result = processor.analyze_sentiment("This policy will benefit citizens")

# Result: {'label': 'positive', 'score': 0.85}
```

### Generate Embeddings

Create embeddings for similarity comparison:

```python
from analysis.nlp_processor import get_processor

processor = get_processor()
embedding = processor.generate_embedding("Your text here")

# Returns: [0.123, -0.456, 0.789, ...] (384-dimensional vector)
```

## Performance Considerations

### Processing Speed

- **Small batch** (10-20 bills): 1-2 minutes
- **Medium batch** (100 bills): 10-15 minutes
- **Large batch** (1000+ bills): 1-2 hours

### Memory Usage

- spaCy model: ~100 MB
- BERT sentiment model: ~250 MB
- Sentence transformer: ~80 MB
- Total: ~430 MB

### Optimization Tips

1. **Batch Processing**: Use `--batch-size` to control memory
2. **Incremental Processing**: Process new bills only (don't use `--force`)
3. **Filtering**: Use jurisdiction/session filters to limit scope
4. **Database Indexes**: Automatically created for fast queries

## Troubleshooting

### Issue: Models Not Loading

**Error**: `OSError: Model not found`

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue: Out of Memory

**Error**: `RuntimeError: CUDA out of memory` or similar

**Solution**:
- Reduce `--batch-size` parameter
- Process fewer bills at once
- The models will automatically use CPU if GPU not available

### Issue: Slow Processing

**Problem**: Extraction is very slow

**Solutions**:
- Models are loaded once at startup (first extraction may be slow)
- Use larger batch sizes for better throughput
- Ensure you're not reprocessing already-analyzed bills

### Issue: Low Quality Extractions

**Problem**: Statements don't make sense

**Solutions**:
- Check `confidence_score` - filter by score > 0.7
- Verify bill text is complete and properly formatted
- Review entity extraction - should find relevant entities
- Consider the source: some bill text may be poorly structured

## Data Quality

### Quality Indicators

Good extractions have:
- Clear actor (legislative body or official)
- Action verb (shall, must, will, etc.)
- Defined target (people, groups, entities)
- Named entities extracted
- Confidence score > 0.7

### Filtering Tips

```python
# Get high-quality statements only
quality_statements = MicroStatement.objects.filter(
    confidence_score__gte=0.7
).exclude(
    actor=''
).exclude(
    target=''
)

# Get statements with named entities
with_entities = MicroStatement.objects.exclude(
    entities__people=[]
).exclude(
    entities__organizations=[]
)
```

## Integration with OpenStates API

The system integrates with OpenStates data:

1. **Bills**: Extracted from `data.Bill` model
2. **Sessions**: Linked via `LegislativeSession`
3. **Legislators**: Can link via bill sponsorships
4. **Jurisdictions**: State/territory codes

### Data Flow

```
OpenStates API → Database (data.Bill)
                     ↓
              extract_statements command
                     ↓
              NLP Processor
                     ↓
              MicroStatement model
                     ↓
              Web Interface / API
```

## Future Enhancements

Planned features:

1. **Machine Learning Classification**: Train custom models for better accuracy
2. **Topic Modeling**: Automatic topic detection using LDA
3. **Relationship Graphs**: Visualize actor-target relationships
4. **Trend Analysis**: Automated trend detection
5. **Comparison Reports**: Generate PDF reports
6. **Real-time Processing**: Process bills as they're added
7. **Bulk Export**: Export to CSV/JSON for external analysis

## Support

For issues or questions:
1. Check this guide first
2. Review existing GitHub issues
3. Submit new issue with:
   - Command used
   - Error message
   - Sample bill that failed
   - Environment info

## License

Same as openstates.org - see LICENSE file in repository root.
