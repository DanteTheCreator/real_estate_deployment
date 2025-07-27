"""
Report generation service for scraping statistics and results.
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import with fallbacks for Docker compatibility
try:
    from core.config import ScrapingConfig
    from models.statistics import ScrapingStats
except ImportError:
    try:
        from ..core.config import ScrapingConfig
        from ..models.statistics import ScrapingStats
    except ImportError:
        from scraper.core.config import ScrapingConfig
        from scraper.models.statistics import ScrapingStats


class ReportService:
    """Service for generating scraping reports."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize the report service."""
        self.config = config
        self.reports_dir = Path(config.reports_directory)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_report(self, stats: ScrapingStats, output_format: str = "json") -> str:
        """Generate detailed scraping report."""
        try:
            report_data = self._prepare_report_data(stats)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if output_format.lower() == "json":
                filename = self._generate_json_report(report_data, timestamp)
            elif output_format.lower() == "csv":
                filename = self._generate_csv_report(report_data, timestamp)
            elif output_format.lower() == "txt":
                filename = self._generate_text_report(report_data, timestamp)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            self.logger.info(f"Report generated: {filename}")
            return str(filename)
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise
    
    def _prepare_report_data(self, stats: ScrapingStats) -> Dict[str, Any]:
        """Prepare comprehensive report data."""
        config_summary = {
            'max_properties': self.config.max_properties,
            'batch_size': self.config.batch_size,
            'concurrent_languages': self.config.concurrent_languages,
            'enable_deduplication': self.config.enable_deduplication,
            'enable_owner_priority': self.config.enable_owner_priority,
            'enable_image_download': self.config.enable_image_download
        }
        
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'scraper_version': '2.0.0',
                'source': 'myhome.ge'
            },
            'configuration': config_summary,
            'statistics': stats.to_dict(),
            'summary': {
                'total_properties_processed': stats.total_fetched,
                'successful_operations': stats.new_properties + stats.updated_properties,
                'failed_operations': stats.errors,
                'efficiency_metrics': {
                    'success_rate_percent': round(stats.success_rate, 2),
                    'requests_per_minute': round(stats.requests_per_minute, 2) if stats.requests_per_minute else 0,
                    'avg_processing_time_seconds': round(stats.duration_seconds / max(stats.total_fetched, 1), 2) if stats.duration_seconds else 0
                }
            }
        }
    
    def _generate_json_report(self, report_data: Dict, timestamp: str) -> Path:
        """Generate JSON format report."""
        filename = self.reports_dir / f"scraping_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def _generate_csv_report(self, report_data: Dict, timestamp: str) -> Path:
        """Generate CSV format report."""
        filename = self.reports_dir / f"scraping_report_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Section', 'Metric', 'Value'])
            
            # Write statistics
            stats = report_data['statistics']
            for section, data in stats.items():
                if isinstance(data, dict):
                    for metric, value in data.items():
                        writer.writerow([section, metric, value])
                else:
                    writer.writerow(['general', section, data])
            
            # Write configuration
            for metric, value in report_data['configuration'].items():
                writer.writerow(['configuration', metric, value])
        
        return filename
    
    def _generate_text_report(self, report_data: Dict, timestamp: str) -> Path:
        """Generate human-readable text report."""
        filename = self.reports_dir / f"scraping_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            self._write_text_header(f, report_data)
            self._write_text_summary(f, report_data)
            self._write_text_statistics(f, report_data)
            self._write_text_configuration(f, report_data)
            self._write_text_breakdown(f, report_data)
        
        return filename
    
    def _write_text_header(self, f, report_data: Dict) -> None:
        """Write report header."""
        f.write("=" * 60 + "\n")
        f.write("MyHome.ge Property Scraper Report\n")
        f.write("=" * 60 + "\n\n")
        
        metadata = report_data['metadata']
        f.write(f"Generated: {metadata['generated_at']}\n")
        f.write(f"Scraper Version: {metadata['scraper_version']}\n")
        f.write(f"Source: {metadata['source']}\n\n")
    
    def _write_text_summary(self, f, report_data: Dict) -> None:
        """Write summary section."""
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 20 + "\n")
        
        stats = report_data['statistics']
        session = stats['session']
        processing = stats['processing']
        
        f.write(f"Session Duration: {session.get('duration_minutes', 0):.2f} minutes\n")
        f.write(f"Properties Processed: {processing['total_fetched']}\n")
        f.write(f"New Properties: {processing['new_properties']}\n")
        f.write(f"Updated Properties: {processing['updated_properties']}\n")
        f.write(f"Success Rate: {processing['success_rate']}%\n")
        f.write(f"Errors: {processing['errors']}\n\n")
    
    def _write_text_statistics(self, f, report_data: Dict) -> None:
        """Write detailed statistics."""
        f.write("DETAILED STATISTICS\n")
        f.write("-" * 20 + "\n")
        
        stats = report_data['statistics']
        
        # Processing stats
        processing = stats['processing']
        f.write("Processing:\n")
        for key, value in processing.items():
            formatted_key = key.replace('_', ' ').title()
            f.write(f"  {formatted_key}: {value}\n")
        f.write("\n")
        
        # Technical stats
        technical = stats['technical']
        f.write("Technical:\n")
        for key, value in technical.items():
            if value is not None:
                formatted_key = key.replace('_', ' ').title()
                f.write(f"  {formatted_key}: {value}\n")
        f.write("\n")
    
    def _write_text_configuration(self, f, report_data: Dict) -> None:
        """Write configuration section."""
        f.write("CONFIGURATION\n")
        f.write("-" * 15 + "\n")
        
        config = report_data['configuration']
        for key, value in config.items():
            formatted_key = key.replace('_', ' ').title()
            f.write(f"{formatted_key}: {value}\n")
        f.write("\n")
    
    def _write_text_breakdown(self, f, report_data: Dict) -> None:
        """Write breakdown section."""
        f.write("BREAKDOWN BY TYPE\n")
        f.write("-" * 18 + "\n")
        
        breakdown = report_data['statistics']['breakdown']
        
        # Languages
        languages = breakdown.get('languages_processed', [])
        if languages:
            f.write(f"Languages Processed: {', '.join(languages)}\n")
        
        # Property types
        property_types = breakdown.get('property_types_processed', {})
        if property_types:
            f.write("\nProperty Types:\n")
            for prop_type, count in property_types.items():
                f.write(f"  {prop_type.replace('_', ' ').title()}: {count}\n")
        
        # Deal types
        deal_types = breakdown.get('deal_types_processed', {})
        if deal_types:
            f.write("\nDeal Types:\n")
            for deal_type, count in deal_types.items():
                f.write(f"  {deal_type.replace('_', ' ').title()}: {count}\n")
    
    def list_reports(self, limit: int = 10) -> list:
        """List recent reports."""
        try:
            report_files = []
            for file_path in self.reports_dir.glob("scraping_report_*.json"):
                stat = file_path.stat()
                report_files.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size_bytes': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            
            # Sort by creation time (newest first)
            report_files.sort(key=lambda x: x['created_at'], reverse=True)
            
            return report_files[:limit]
            
        except Exception as e:
            self.logger.error(f"Error listing reports: {e}")
            return []
    
    def cleanup_old_reports(self, keep_days: int = 30) -> int:
        """Remove old report files."""
        try:
            cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
            removed_count = 0
            
            for file_path in self.reports_dir.glob("scraping_report_*"):
                if file_path.stat().st_ctime < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old report files")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up reports: {e}")
            return 0
