"""
Statistics tracking for scraping operations.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ScrapingStats:
    """Statistics for scraping operations."""
    
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Processing counts
    total_fetched: int = 0
    new_properties: int = 0
    updated_properties: int = 0
    duplicates_skipped: int = 0
    owner_prioritized: int = 0
    agency_discarded: int = 0
    cleaned_old: int = 0
    errors: int = 0
    
    # Technical stats
    api_calls: int = 0
    failed_requests: int = 0
    
    # Language processing
    languages_processed: List[str] = field(default_factory=list)
    
    # Property type breakdown
    property_types_processed: Dict[str, int] = field(default_factory=dict)
    
    # Deal type breakdown
    deal_types_processed: Dict[str, int] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate duration in minutes."""
        seconds = self.duration_seconds
        return seconds / 60 if seconds is not None else None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_fetched == 0:
            return 0.0
        return ((self.new_properties + self.updated_properties) / self.total_fetched) * 100
    
    @property
    def requests_per_minute(self) -> Optional[float]:
        """Calculate requests per minute."""
        duration_min = self.duration_minutes
        if duration_min and duration_min > 0:
            return self.api_calls / duration_min
        return None
    
    def add_property_type(self, property_type: str) -> None:
        """Track a property type."""
        if property_type not in self.property_types_processed:
            self.property_types_processed[property_type] = 0
        self.property_types_processed[property_type] += 1
    
    def add_deal_type(self, deal_type: str) -> None:
        """Track a deal type."""
        if deal_type not in self.deal_types_processed:
            self.deal_types_processed[deal_type] = 0
        self.deal_types_processed[deal_type] += 1
    
    def to_dict(self) -> Dict:
        """Convert statistics to dictionary for reporting."""
        return {
            'session': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': self.duration_seconds,
                'duration_minutes': self.duration_minutes
            },
            'processing': {
                'total_fetched': self.total_fetched,
                'new_properties': self.new_properties,
                'updated_properties': self.updated_properties,
                'duplicates_skipped': self.duplicates_skipped,
                'owner_prioritized': self.owner_prioritized,
                'agency_discarded': self.agency_discarded,
                'cleaned_old': self.cleaned_old,
                'errors': self.errors,
                'success_rate': round(self.success_rate, 2)
            },
            'technical': {
                'api_calls': self.api_calls,
                'failed_requests': self.failed_requests,
                'requests_per_minute': round(self.requests_per_minute, 2) if self.requests_per_minute else None
            },
            'breakdown': {
                'languages_processed': self.languages_processed,
                'property_types_processed': self.property_types_processed,
                'deal_types_processed': self.deal_types_processed
            }
        }
