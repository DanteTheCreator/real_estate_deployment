# Advanced MyHome.ge Property Scraper (Refactored)

A modular, production-ready scraper for MyHome.ge property data with advanced features including multilingual support, deduplication, and comprehensive error handling.

## 🏗️ Architecture

The scraper has been refactored into a modular architecture with clear separation of concerns:

```
scraper/
├── core/                   # Core framework components
│   ├── config.py          # Configuration management
│   ├── base_scraper.py    # Abstract base scraper
│   └── exceptions.py      # Custom exceptions
├── models/                 # Data models
│   ├── statistics.py      # Statistics tracking
│   └── property_data.py   # Property data structures
├── processors/            # Data processing components
│   ├── data_processor.py        # Basic data processing
│   ├── multilingual_processor.py # Multilingual content
│   ├── image_processor.py       # Image handling
│   ├── price_processor.py       # Price and currency
│   └── parameter_processor.py   # Parameters/amenities
├── services/              # Business logic services
│   ├── database_service.py      # Database operations
│   ├── deduplication_service.py # Duplicate detection
│   ├── exchange_rate_service.py # Currency conversion
│   └── report_service.py        # Report generation
├── utils/                 # Utility functions
│   ├── validation.py      # Data validation
│   └── helpers.py         # Helper functions
├── myhome_scraper.py      # Main scraper class
└── main.py               # CLI entry point
```

## 🚀 Features

### Core Features
- **Modular Architecture**: Clean separation of concerns for easy maintenance and extension
- **Asynchronous Processing**: Efficient concurrent processing of properties
- **Comprehensive Error Handling**: Robust error handling with detailed logging
- **Rate Limiting**: Built-in rate limiting to avoid being blocked
- **Configuration Management**: Flexible configuration via files or environment variables

### Advanced Features
- **Multilingual Support**: Extract content in Georgian, English, and Russian
- **Smart Deduplication**: Advanced duplicate detection with owner priority
- **Image Processing**: Download and manage property images
- **Currency Conversion**: Automatic currency conversion with real-time rates
- **Data Validation**: Comprehensive data quality validation
- **Reporting**: Detailed reports in JSON, CSV, or text format

## 📋 Requirements

- Python 3.8+
- PostgreSQL database
- Required Python packages (see requirements.txt):
  - aiohttp
  - requests
  - sqlalchemy
  - pyyaml
  - asyncio

## 🛠️ Installation

1. **Install dependencies**:
```bash
pip install aiohttp requests sqlalchemy pyyaml
```

2. **Configure database**: Ensure your PostgreSQL database is set up and accessible.

3. **Set up configuration**: Create a configuration file or set environment variables.

## ⚙️ Configuration

### Configuration File (YAML)
Create a `config.yaml` file:

```yaml
# Basic scraping settings
max_properties: 1000
batch_size: 50
delay_between_requests: 0.1
max_retries: 3
timeout: 30

# Feature toggles
concurrent_languages: true
enable_image_download: false
enable_deduplication: true
enable_owner_priority: true

# Storage paths
image_storage_path: "/app/data/property_images"
log_directory: "/app/logs"
reports_directory: "/app/data/reports"
```

### Environment Variables
```bash
export SCRAPER_MAX_PROPERTIES=1000
export SCRAPER_BATCH_SIZE=50
export SCRAPER_CONCURRENT_LANGUAGES=true
export SCRAPER_ENABLE_DEDUP=true
```

## 🎯 Usage

### Command Line Interface

Basic usage:
```bash
python main.py --mode full --max-properties 500
```

With configuration file:
```bash
python main.py --config config.yaml --report-format json
```

Advanced options:
```bash
python main.py \
  --mode incremental \
  --property-type 1 \
  --enable-images \
  --no-multilingual \
  --batch-size 25 \
  --delay 0.2 \
  --report-format csv
```

### Programmatic Usage

```python
import asyncio
from scraper import MyHomeAdvancedScraper, ScrapingConfig, ScrapingMode

# Create configuration
config = ScrapingConfig(
    max_properties=500,
    concurrent_languages=True,
    enable_deduplication=True
)

# Create and run scraper
async def run_scraper():
    scraper = MyHomeAdvancedScraper(config)
    try:
        stats = await scraper.scrape(ScrapingMode.FULL)
        print(f"Processed {stats.total_fetched} properties")
        
        # Generate report
        report_file = scraper.generate_report("json")
        print(f"Report saved: {report_file}")
        
    finally:
        scraper.finalize()

# Run the scraper
asyncio.run(run_scraper())
```

### Simple Usage
```python
from scraper import scrape_properties, ScrapingConfig

# Quick scraping with default config
stats = await scrape_properties()

# With custom configuration
config = ScrapingConfig(max_properties=100)
stats = await scrape_properties(config)
```

## 📊 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Scraping mode (full, incremental, specific_type, validation) | full |
| `--config` | Path to YAML configuration file | None |
| `--max-properties` | Maximum properties to scrape | 1000 |
| `--batch-size` | API request batch size | 50 |
| `--delay` | Delay between requests (seconds) | 0.1 |
| `--property-type` | Filter by property type (1-6) | None |
| `--deal-type` | Filter by deal type (1,2,3,7) | None |
| `--no-multilingual` | Disable multilingual processing | False |
| `--enable-images` | Enable image download | False |
| `--report-format` | Report format (json, csv, txt) | json |
| `--dry-run` | Run without saving to database | False |

## 🔧 Extending the Scraper

### Adding New Processors

1. Create a new processor in the `processors/` directory:

```python
# processors/my_processor.py
class MyProcessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, property_data, raw_data):
        # Your processing logic here
        pass
```

2. Add it to the main scraper:

```python
# In myhome_scraper.py
from .processors import MyProcessor

class MyHomeAdvancedScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.my_processor = MyProcessor(config)
```

### Adding New Services

1. Create a service in the `services/` directory:

```python
# services/my_service.py
class MyService:
    def __init__(self, config):
        self.config = config
    
    def do_something(self):
        # Your service logic here
        pass
```

2. Integrate it into the scraper workflow.

### Custom Validators

Add custom validation rules:

```python
from scraper.utils import PropertyValidator

class CustomValidator(PropertyValidator):
    def validate_custom_field(self, value):
        # Custom validation logic
        return True
```

## 📈 Monitoring and Logging

The scraper provides comprehensive logging and statistics:

### Log Levels
- **DEBUG**: Detailed processing information
- **INFO**: General progress updates
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors that need attention

### Statistics Tracking
- Properties processed, new, updated
- Duplicate detection stats
- Error counts and rates
- Performance metrics
- Language and type breakdowns

### Reports
Generated reports include:
- Session information
- Processing statistics
- Configuration summary
- Breakdown by property/deal types
- Performance metrics

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check PostgreSQL connection settings
   - Verify database credentials
   - Ensure database exists and is accessible

2. **Rate Limiting**
   - Increase delay between requests
   - Reduce batch size
   - Check rate limit configuration

3. **Memory Issues**
   - Reduce max properties per run
   - Disable image download if not needed
   - Increase batch processing delays

4. **Validation Errors**
   - Check coordinate bounds in config
   - Verify price range settings
   - Review validation logs for details

### Debug Mode
Run with debug logging:
```bash
python main.py --log-level DEBUG --max-properties 10
```

### Dry Run Mode
Test without saving to database:
```bash
python main.py --dry-run --max-properties 50
```

## 🤝 Contributing

1. Follow the modular architecture
2. Add appropriate logging
3. Include error handling
4. Write unit tests for new components
5. Update documentation

## 📄 License

This project is licensed under the MIT License.

## 🔗 API Reference

### Core Classes

- **ScrapingConfig**: Configuration management
- **ScrapingMode**: Enumeration of scraping modes
- **BaseScraper**: Abstract base class for scrapers
- **MyHomeAdvancedScraper**: Main scraper implementation

### Data Models

- **PropertyData**: Comprehensive property data structure
- **ScrapingStats**: Statistics tracking and reporting
- **PropertyImage**: Image data structure
- **PropertyPrice**: Price information structure

### Services

- **DatabaseService**: Database operations
- **DeduplicationService**: Duplicate detection and handling
- **ExchangeRateService**: Currency conversion
- **ReportService**: Report generation

For detailed API documentation, see the docstrings in the source code.
