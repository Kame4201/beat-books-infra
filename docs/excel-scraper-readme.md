# Excel URL Scraper - Implementation Guide

## Overview

This implementation adds a new Excel-based URL scraper that reads Pro-Football-Reference URLs from an Excel file, scrapes the data tables, and stores them in the Neon PostgreSQL database.

## Features

✅ **Excel Input**: Reads URLs and metadata from `.xlsx` files
✅ **Dynamic Table Extraction**: Automatically finds and parses all stat tables on each page
✅ **Comment Parsing**: Handles tables hidden in HTML comments (common on PFR)
✅ **Metadata Tracking**: Adds `source_url`, `scraped_at`, and custom metadata to each record
✅ **Idempotent Upserts**: Deletes existing data from the same URL before inserting (prevents duplicates)
✅ **Error Handling**: Gracefully handles failures and continues processing remaining URLs
✅ **Dynamic Schema**: Auto-creates database tables based on DataFrame structure

## Files Added/Modified

### New Files
- `src/services/excel_scraper_service.py` - Core scraping logic
- `sample_urls.xlsx` - Example Excel file
- `test_create_sample_excel.py` - Script to create sample Excel files
- `test_excel_scraper.py` - Test suite
- `EXCEL_SCRAPER_README.md` - This file

### Modified Files
- `src/main.py` - Added `/scrape/excel` endpoint
- `src/requirements.txt` - Added `openpyxl` dependency

## Excel File Format

The Excel file should contain the following columns:

### Required
- **`url`** (string): The Pro-Football-Reference URL to scrape

### Optional
- **`season`** (integer): Season year (e.g., 2024)
- **`entity_type`** (string): Type of entity (e.g., "team", "league", "player")
- **`table_type`** (string): Type of table (e.g., "schedule", "stats", "roster")

### Example

| url | season | entity_type | table_type |
|-----|--------|-------------|------------|
| https://www.pro-football-reference.com/teams/buf/2024.htm | 2024 | team | schedule |
| https://www.pro-football-reference.com/teams/kan/2024.htm | 2024 | team | schedule |
| https://www.pro-football-reference.com/years/2024/ | 2024 | league | team_stats |

## API Usage

### Endpoint
```
POST /scrape/excel?excel_path=/path/to/file.xlsx
```

### Example Request
```bash
curl -X POST "http://localhost:8000/scrape/excel?excel_path=sample_urls.xlsx"
```

### Example Response
```json
{
  "urls_processed": 3,
  "urls_success": 3,
  "urls_failed": 0,
  "tables_extracted": 15,
  "rows_inserted": 450,
  "errors": []
}
```

## Database Schema

Tables are created dynamically with the pattern: `scraped_{table_id}`

Each table includes:
- **`id`** (SERIAL PRIMARY KEY): Auto-incremented ID
- **Original columns** from the scraped table (data types inferred)
- **`source_url`** (TEXT): The URL the data came from
- **`scraped_at`** (TIMESTAMP): When the data was scraped
- **`season`** (INTEGER, optional): Season year if provided
- **`entity_type`** (TEXT, optional): Entity type if provided
- **`table_type`** (TEXT, optional): Table type if provided

### Example Table: `scraped_team_stats`
```sql
CREATE TABLE scraped_team_stats (
    id SERIAL PRIMARY KEY,
    rk INTEGER,
    tm TEXT,
    g INTEGER,
    pf INTEGER,
    ...
    source_url TEXT,
    scraped_at TIMESTAMP,
    season INTEGER,
    entity_type TEXT,
    table_type TEXT
);
```

## Implementation Details

### 1. Excel Reading (`read_excel_urls`)
- Reads all sheets from the Excel file
- Combines them into a single DataFrame
- Validates that `url` column exists
- Removes rows with empty URLs

### 2. Table Extraction (`extract_tables_from_url`)
- Fetches HTML from URL with enhanced headers
- Extracts visible tables using BeautifulSoup
- Parses HTML comments to find hidden tables (PFR technique)
- Converts tables to pandas DataFrames
- Flattens MultiIndex columns

### 3. Metadata Addition (`add_metadata_columns`)
- Adds `source_url` and `scraped_at` to every row
- Adds optional metadata from Excel file

### 4. Database Operations
- **`create_table_if_not_exists`**: Dynamically creates tables based on DataFrame structure
- **`upsert_dataframe`**: Deletes existing data from same URL, then inserts new data

### 5. Main Function (`scrape_from_excel`)
- Orchestrates the entire pipeline
- Handles errors gracefully
- Returns detailed summary

## Known Limitations & Solutions

### Pro-Football-Reference Bot Detection

⚠️ **Issue**: Pro-Football-Reference has aggressive bot detection that may block requests.

**Solutions**:

1. **Use Selenium** (recommended for production):
   ```python
   # The existing scrape_service.py uses Selenium successfully
   # Consider hybrid approach: use Selenium for fetching, pandas for parsing
   ```

2. **Add Request Sessions**:
   ```python
   session = requests.Session()
   session.get('https://www.pro-football-reference.com/')  # Get cookies first
   time.sleep(3)  # Then use session for subsequent requests
   ```

3. **Use Residential Proxies**: Route requests through proxy services

4. **Rate Limiting**: Already implemented (2 second delay between requests)

### Testing Without Live Scraping

The implementation has been tested with:
- ✅ Excel reading logic
- ✅ DataFrame manipulation
- ✅ Metadata addition
- ✅ Database table creation logic
- ⚠️ Live scraping (blocked by PFR in test environment)

## Production Recommendations

1. **Selenium Integration**: For production use, consider integrating Selenium like the existing `scrape_service.py`

2. **Caching**: Implement caching to avoid re-scraping same URLs

3. **Logging**: Add proper logging (replace `print` statements)

4. **Async Processing**: For large Excel files, consider background task processing (Celery, etc.)

5. **Schema Validation**: Add validation for expected table structures

6. **Primary Keys**: Implement smart primary key detection based on table type

## Code Quality

- ✅ Type hints on all functions
- ✅ Docstrings with parameter descriptions
- ✅ Error handling with graceful degradation
- ✅ Follows existing code patterns (repository, session management)
- ✅ No framework changes (uses existing SQLAlchemy, FastAPI)
- ✅ Respects existing database connection

## Testing

Run the test suite:
```bash
python test_excel_scraper.py
```

Create sample Excel file:
```bash
python test_create_sample_excel.py
```

## Future Enhancements

- [ ] Add support for file upload (not just file path)
- [ ] Add progress tracking for long-running scrapes
- [ ] Add retry logic with exponential backoff
- [ ] Support for CSV input in addition to Excel
- [ ] Web UI for uploading Excel files
- [ ] Scheduled scraping (cron jobs)
- [ ] Data validation before insertion
