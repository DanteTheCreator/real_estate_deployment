# Scraper Database Integration

This module enables the property scraper to save data directly to the backend database.

## Features

- **Smart Duplicate Detection**: Uses multiple methods to detect existing properties:
  - External ID matching (most reliable)
  - Address + area + price fuzzy matching
  - GPS coordinate-based location matching
- **Enhanced Database Schema**: Added new fields for scraped properties:
  - `external_id`: Original property ID from source
  - `source`: Source website (e.g., "myhome.ge")
  - `district`, `urban_area`: Location details
  - `latitude`, `longitude`: GPS coordinates
  - `floor_number`, `total_floors`: Floor information
  - `user_type`: Owner type (physical/agent)
  - `last_scraped`: Timestamp of last scrape
- **Batch Processing**: Efficient database operations with configurable batch sizes
- **Error Handling**: Robust error handling with detailed logging

## Setup

### 1. Install Dependencies

```bash
cd scraper
pip install -r requirements.txt
```

### 2. Run Database Migration

Before first use, run the migration to add new columns:

```bash
python migrate_db.py
```

### 3. Test Database Connection

```bash
python database_integration.py
```

## Usage

### Quick Start (Test Mode)

```bash
# Run scraper in test mode (3 pages only)
python scrape_to_db.py --test-mode
```

### Full Scraping

```bash
# Scrape all pages and save to database
python scrape_to_db.py

# Scrape with custom settings
python scrape_to_db.py --max-pages 50 --delay 2.0 --batch-size 50
```

### Advanced Options

```bash
# Clean existing data and start fresh
python scrape_to_db.py --cleanup-first --test-mode

# Allow duplicates (don't skip existing)
python scrape_to_db.py --no-skip-existing

# Don't save JSON files (database only)
python scrape_to_db.py --no-save-files

# Verbose logging
python scrape_to_db.py --verbose --test-mode
```

## File Structure

```
scraper/
├── enhanced_scraper.py        # Main scraper logic
├── database_integration.py   # Database integration module
├── scrape_to_db.py           # Combined scraper + database script
├── migrate_db.py             # Database migration script
├── requirements.txt          # Dependencies
└── README_DATABASE.md        # This file
```

## Database Schema

The enhanced Property model includes these new fields:

| Field | Type | Description |
|-------|------|-------------|
| `external_id` | String | Original property ID from source site |
| `source` | String | Source website (e.g., "myhome.ge") |
| `district` | String | District/area name |
| `urban_area` | String | Urban/neighborhood name |
| `latitude` | Float | GPS latitude |
| `longitude` | Float | GPS longitude |
| `floor_number` | Integer | Floor number |
| `total_floors` | Integer | Total floors in building |
| `user_type` | String | Owner type ("physical" or "agent") |
| `last_scraped` | DateTime | Last scrape timestamp |

## Duplicate Detection Logic

The system uses a three-tier approach to detect duplicates:

1. **External ID Match**: Exact match on `external_id` + `source`
2. **Fuzzy Address Match**: Normalized address + area + price comparison
3. **Location Match**: GPS coordinates + area + price tolerance

This ensures that properties are not duplicated even if they appear with slight variations.

## System User

The integration creates a special "system" user (`system@scraper.internal`) that owns all scraped properties. This user:
- Cannot log in (password: "no_login")
- Has role "system"
- Is used to identify scraped vs. manually entered properties

## Monitoring

The script provides detailed statistics including:
- Number of properties scraped vs. saved
- Duplicate detection results
- Database operation statistics
- Error counts and details

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check database URL in backend config
- Verify database credentials

### Import Errors
- Run from scraper directory
- Ensure backend dependencies are installed
- Check that backend directory is accessible

### Migration Issues
- Run migration script before first use
- Check database permissions
- Ensure no conflicting schema changes

## Example Output

```
================================================================================
SCRAPER TO DATABASE PIPELINE RESULTS
================================================================================

SCRAPING STATISTICS:
  Raw properties fetched: 1250
  Unique properties after deduplication: 950
  Duplicates removed by scraper: 300

DATABASE STATISTICS:
  Properties before scraping: 45
  Properties after scraping: 892
  New properties added: 847
  Existing properties skipped: 103
  Errors during save: 0
  Total processed: 950
```
