#!/bin/bash

# Real Estate Scraper Cron Script
# This script runs the property scraper with proper environment setup

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up environment
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
export PYTHONUNBUFFERED=1

# Set database URL if needed (adjust as necessary)
export DATABASE_URL="${DATABASE_URL:-postgresql://real-estate-user:real-estate-password@localhost:5432/real-estate-rental}"

# Log file for cron output
LOG_FILE="${SCRIPT_DIR}/logs/cron_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory if it doesn't exist
mkdir -p "${SCRIPT_DIR}/logs"

# Run the scraper with logging
echo "$(date): Starting Real Estate Scraper" >> "$LOG_FILE"
cd "$SCRIPT_DIR"

# Try to activate virtual environment if it exists
if [ -f "${SCRIPT_DIR}/venv/bin/activate" ]; then
    source "${SCRIPT_DIR}/venv/bin/activate"
    echo "$(date): Activated virtual environment" >> "$LOG_FILE"
fi

# Run the scraper
python3 "${SCRIPT_DIR}/run_scraper.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "$(date): Scraper finished with exit code $EXIT_CODE" >> "$LOG_FILE"

# Send notification on failure (optional)
if [ $EXIT_CODE -ne 0 ]; then
    echo "$(date): ERROR - Scraper failed with exit code $EXIT_CODE" >> "$LOG_FILE"
    # Uncomment the next line to send email notifications on failure
    # echo "Real Estate Scraper failed with exit code $EXIT_CODE" | mail -s "Scraper Failure" admin@yourdomain.com
fi

exit $EXIT_CODE
