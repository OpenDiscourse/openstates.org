# Bulk Data Ingestion CLI Reference

Complete reference for the `bulk_ingest` management command.

## Command Syntax

```bash
python manage.py bulk_ingest [OPTIONS]
```

## Options

### `--connection-string <string>`
Specify a database connection string for the target database.

**Format**: `postgresql://user:password@host:port/database`

**Examples**:
```bash
--connection-string "postgresql://admin:secret@localhost:5432/openstates"
--connection-string "postgresql://user:pass@cloudcurio.cc:5432/analysis_db"
```

**Default**: Uses current Django database configuration from `DATABASE_URL` environment variable.

### `--jurisdictions <list>`
Comma-separated list of jurisdiction abbreviations to ingest.

**Format**: Two-letter state codes separated by commas (no spaces)

**Examples**:
```bash
--jurisdictions "tx"           # Texas only
--jurisdictions "tx,ca,ny"     # Texas, California, New York
--jurisdictions "all"          # All available jurisdictions
```

**Default**: All jurisdictions if not specified.

### `--data-types <list>`
Comma-separated list of data types to ingest.

**Available Types**:
- `bills` - Legislative bills and related data
- `votes` - Vote events and voting records
- `people` - Legislators and their information
- `organizations` - Legislative bodies and committees
- `all` - All data types

**Examples**:
```bash
--data-types "bills"                    # Bills only
--data-types "bills,votes"              # Bills and votes
--data-types "people,organizations"     # People and organizations
--data-types "all"                      # Everything
```

**Default**: `all`

### `--list-jurisdictions`
List all available jurisdictions and exit. Useful for discovering available state codes.

**Example**:
```bash
python manage.py bulk_ingest --list-jurisdictions
```

**Output**:
```
=== Available Jurisdictions ===

  ak    - Alaska                         (15 sessions)
  al    - Alabama                        (20 sessions)
  ar    - Arkansas                       (18 sessions)
  ...
```

### `--dry-run`
Show what would be ingested without actually performing the operation. Useful for testing and validation.

**Example**:
```bash
python manage.py bulk_ingest --jurisdictions "tx" --dry-run
```

**Output**: Displays summary of data that would be ingested with counts but doesn't modify the database.

### `--verbose`
Enable verbose output with detailed logging information.

**Example**:
```bash
python manage.py bulk_ingest --jurisdictions "tx" --verbose
```

**Output**: Shows debug-level information including:
- Connection details
- Query execution
- Progress updates
- Detailed error messages

## Usage Examples

### Example 1: List Available Jurisdictions

```bash
python manage.py bulk_ingest --list-jurisdictions
```

### Example 2: Ingest Texas Data (Dry Run)

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx" \
    --data-types "all" \
    --dry-run
```

### Example 3: Ingest Bills and Votes for Multiple States

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx,ca,ny,fl" \
    --data-types "bills,votes"
```

### Example 4: Ingest to External Database

```bash
python manage.py bulk_ingest \
    --connection-string "postgresql://user:pass@cloudcurio.cc:5432/openstates_analysis" \
    --jurisdictions "tx,ca" \
    --data-types "all"
```

### Example 5: Verbose Ingestion with Logging

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx" \
    --data-types "bills" \
    --verbose
```

### Example 6: Ingest All Data for All Jurisdictions

```bash
python manage.py bulk_ingest \
    --jurisdictions "all" \
    --data-types "all"
```

⚠️ **Warning**: This will ingest the complete OpenStates database and may take several hours.

### Example 7: Ingest Only Legislators

```bash
python manage.py bulk_ingest \
    --jurisdictions "tx,ca,ny" \
    --data-types "people"
```

## Output Format

### Success Output

```
=== Bulk Data Ingestion ===
Jurisdictions: tx, ca, ny
Data types: bills, votes
Mode: LIVE

Ingesting bills...
  Texas - 2023: 5234 bills
  California - 2023-2024: 3421 bills
  New York - 2023-2024: 2134 bills

Ingesting votes...
  Texas - 2023: 12456 votes
  California - 2023-2024: 8234 votes
  New York - 2023-2024: 6543 votes

=== Ingestion Complete ===
Total bills: 10789
Total votes: 27233
Total people: 0
Total organizations: 0
```

### Error Output

```
Error: Invalid jurisdiction code 'xx'
Valid codes: tx, ca, ny, fl, ...

Use --list-jurisdictions to see all available jurisdictions.
```

## Database Connection Strings

### PostgreSQL

```bash
--connection-string "postgresql://username:password@hostname:5432/database"
```

**Components**:
- `postgresql://` - Protocol (also accepts `postgres://`)
- `username` - Database user
- `password` - User password
- `hostname` - Database host (IP or domain)
- `5432` - Port number (default for PostgreSQL)
- `database` - Database name

### MySQL (Future Support)

```bash
--connection-string "mysql://username:password@hostname:3306/database"
```

**Note**: MySQL support requires additional configuration.

### Local Development

```bash
--connection-string "postgresql://openstates:openstates@localhost:5432/openstatesorg"
```

### Docker Container

```bash
--connection-string "postgresql://openstates:openstates@db:5432/openstatesorg"
```

**Note**: Use service name `db` as hostname when running inside Docker.

### Cloud Services

#### AWS RDS
```bash
--connection-string "postgresql://user:pass@my-db.abc123.us-east-1.rds.amazonaws.com:5432/openstates"
```

#### Google Cloud SQL
```bash
--connection-string "postgresql://user:pass@10.0.0.1:5432/openstates"
```

#### Azure Database
```bash
--connection-string "postgresql://user@server:pass@server.postgres.database.azure.com:5432/openstates"
```

#### Custom Domain (cloudcurio.cc)
```bash
--connection-string "postgresql://admin:password@cloudcurio.cc:5432/analysis"
```

## Environment Variables

Instead of passing `--connection-string`, you can set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db"
python manage.py bulk_ingest --jurisdictions "tx"
```

## Data Volume Estimates

Approximate data sizes per jurisdiction (as of 2025):

| Jurisdiction | Bills | Votes | People | Organizations |
|--------------|-------|-------|--------|---------------|
| Texas        | 5,000+ | 15,000+ | 181 | 50 |
| California   | 4,000+ | 12,000+ | 120 | 40 |
| New York     | 3,000+ | 10,000+ | 213 | 35 |

**Total (All States)**: ~200,000 bills, ~600,000 votes, ~7,500 people

## Performance Tips

1. **Start Small**: Test with one jurisdiction first
2. **Use Dry Run**: Always test with `--dry-run` first
3. **Filter Data Types**: Only ingest what you need
4. **Monitor Progress**: Use `--verbose` for long operations
5. **Database Indexes**: Ensure target database has proper indexes
6. **Network Latency**: Use local database for faster ingestion
7. **Batch Processing**: Ingest jurisdictions separately for better control

## Logging

Ingestion operations are logged to `DataIngestionLog` model:

```python
from analysis.models import DataIngestionLog

# View recent ingestions
logs = DataIngestionLog.objects.all().order_by('-started_at')[:10]

for log in logs:
    print(f"{log.id}: {log.status} - {log.total_bills} bills")
```

Or view in admin interface: `/djadmin/analysis/dataingestionlog/`

Or view in web dashboard: `/analysis/ingestion-logs/`

## Error Handling

### Connection Errors

**Error**: `django.db.utils.OperationalError: could not connect to server`

**Solutions**:
- Check database is running
- Verify connection string
- Check firewall settings
- Ensure database accepts connections from your IP

### Permission Errors

**Error**: `django.db.utils.ProgrammingError: permission denied`

**Solutions**:
- Verify database user has CREATE/INSERT permissions
- Check user has access to target schema
- Ensure user can read source tables

### Timeout Errors

**Error**: Operation times out

**Solutions**:
- Ingest smaller batches
- Increase timeout settings
- Check network connectivity
- Use local database if possible

## Best Practices

1. **Always Use Dry Run First**
   ```bash
   python manage.py bulk_ingest --jurisdictions "tx" --dry-run
   ```

2. **Test Connection String**
   ```bash
   python manage.py dbshell  # Should connect successfully
   ```

3. **Monitor Disk Space**
   ```bash
   df -h  # Check available disk space
   ```

4. **Backup Before Ingestion**
   ```bash
   pg_dump openstates > backup.sql
   ```

5. **Use Transactions** (automatic in Django)
   - Ingestion is atomic per data type
   - Failed operations are rolled back

6. **Schedule Regular Updates**
   ```bash
   # Cron job example (daily at 2 AM)
   0 2 * * * cd /path/to/openstates.org && python manage.py bulk_ingest --jurisdictions "all"
   ```

## Troubleshooting

### Issue: No data ingested

**Check**:
1. Database connection successful?
2. Source data exists?
3. Proper permissions?
4. Check logs for errors

### Issue: Partial data ingested

**Check**:
1. Review error messages
2. Check DataIngestionLog status
3. Verify data types specified correctly
4. Ensure disk space available

### Issue: Slow performance

**Solutions**:
1. Use local database
2. Increase database resources
3. Ingest fewer jurisdictions at once
4. Optimize network connection
5. Use SSD storage

## Support

For help:
- Run: `python manage.py bulk_ingest --help`
- Check logs: `/analysis/ingestion-logs/`
- Read docs: `analysis/README.md`
- View examples: `ANALYSIS_DEMO.md`

## Related Commands

- `python manage.py migrate` - Apply database migrations
- `python manage.py dbshell` - Access database shell
- `python manage.py runserver` - Start development server
- `python manage.py test analysis` - Run tests

## Version History

- **v1.0** (2025-11-10): Initial release with basic ingestion functionality
- Future: Add incremental updates, change detection, parallel processing
