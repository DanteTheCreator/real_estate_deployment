#!/usr/bin/env python3
import sys
sys.path.append('/app')

from scraper.core.config import ScrapingConfig

config = ScrapingConfig()
print(f"concurrent_languages type: {type(config.concurrent_languages)}")
print(f"concurrent_languages value: {config.concurrent_languages}")
print(f"concurrent_languages repr: {repr(config.concurrent_languages)}")
print(f"bool(concurrent_languages): {bool(config.concurrent_languages)}")

# Check all config attributes
print("\nAll config attributes:")
for attr in dir(config):
    if not attr.startswith('_'):
        value = getattr(config, attr)
        if not callable(value):
            print(f"  {attr}: {value} ({type(value)})")
