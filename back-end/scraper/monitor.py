#!/usr/bin/env python3
"""
Monitoring and health check script for the MyHome.ge scraper.
"""

import os
import sys
import time
import json
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

class ScraperMonitor:
    """Monitor scraper health and performance"""
    
    def __init__(self):
        self.logs_dir = Path("/app/logs")
        self.reports_dir = Path("/app/data/reports")
        self.alerts_file = Path("/app/data/alerts.json")
        
    def check_scraper_process(self) -> Dict[str, Any]:
        """Check if scraper process is running"""
        status = {
            'running': False,
            'processes': [],
            'memory_usage': 0,
            'cpu_usage': 0
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
            try:
                if 'advanced_myhome_scraper.py' in ' '.join(proc.info['cmdline'] or []):
                    status['running'] = True
                    status['processes'].append({
                        'pid': proc.info['pid'],
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                        'cpu_percent': proc.info['cpu_percent']
                    })
                    status['memory_usage'] += proc.info['memory_info'].rss / 1024 / 1024
                    status['cpu_usage'] += proc.info['cpu_percent'] or 0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return status
    
    def check_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Check for recent scraping activity"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        activity = {
            'recent_logs': False,
            'recent_reports': False,
            'last_log_time': None,
            'last_report_time': None,
            'log_count': 0,
            'report_count': 0
        }
        
        # Check logs
        if self.logs_dir.exists():
            for log_file in self.logs_dir.glob("*.log"):
                mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mod_time > cutoff_time:
                    activity['recent_logs'] = True
                    activity['log_count'] += 1
                    if not activity['last_log_time'] or mod_time > activity['last_log_time']:
                        activity['last_log_time'] = mod_time
        
        # Check reports
        if self.reports_dir.exists():
            for report_file in self.reports_dir.glob("*.json"):
                mod_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                if mod_time > cutoff_time:
                    activity['recent_reports'] = True
                    activity['report_count'] += 1
                    if not activity['last_report_time'] or mod_time > activity['last_report_time']:
                        activity['last_report_time'] = mod_time
        
        return activity
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Check database connectivity"""
        status = {
            'connected': False,
            'error': None,
            'response_time': None
        }
        
        try:
            start_time = time.time()
            result = subprocess.run([
                'pg_isready', 
                '-h', os.getenv('POSTGRES_HOST', 'postgres'),
                '-p', os.getenv('POSTGRES_PORT', '5432'),
                '-U', os.getenv('POSTGRES_USER', 'postgres')
            ], capture_output=True, timeout=10)
            
            status['response_time'] = time.time() - start_time
            status['connected'] = result.returncode == 0
            
            if result.returncode != 0:
                status['error'] = result.stderr.decode()
        except subprocess.TimeoutExpired:
            status['error'] = "Database connection timeout"
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        status = {
            'total_gb': 0,
            'used_gb': 0,
            'free_gb': 0,
            'usage_percent': 0,
            'warning': False
        }
        
        try:
            disk_usage = psutil.disk_usage('/app')
            status['total_gb'] = disk_usage.total / (1024**3)
            status['used_gb'] = disk_usage.used / (1024**3)
            status['free_gb'] = disk_usage.free / (1024**3)
            status['usage_percent'] = (disk_usage.used / disk_usage.total) * 100
            status['warning'] = status['usage_percent'] > 80
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def analyze_latest_report(self) -> Dict[str, Any]:
        """Analyze the latest scraping report"""
        analysis = {
            'has_report': False,
            'success_rate': 0,
            'error_rate': 0,
            'properties_processed': 0,
            'duration_minutes': 0,
            'languages_processed': [],
            'warnings': []
        }
        
        if not self.reports_dir.exists():
            return analysis
        
        # Find latest report
        reports = list(self.reports_dir.glob("*.json"))
        if not reports:
            return analysis
        
        latest_report = max(reports, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_report) as f:
                data = json.load(f)
            
            analysis['has_report'] = True
            stats = data.get('statistics', {})
            
            analysis['properties_processed'] = stats.get('total_fetched', 0)
            analysis['error_rate'] = stats.get('errors', 0)
            
            if analysis['properties_processed'] > 0:
                success_count = stats.get('new_properties', 0) + stats.get('updated_properties', 0)
                analysis['success_rate'] = (success_count / analysis['properties_processed']) * 100
            
            session_info = data.get('scraping_session', {})
            analysis['duration_minutes'] = session_info.get('duration_minutes', 0)
            analysis['languages_processed'] = data.get('languages_processed', [])
            
            # Add warnings based on analysis
            if analysis['success_rate'] < 50:
                analysis['warnings'].append("Low success rate")
            if analysis['error_rate'] > 10:
                analysis['warnings'].append("High error rate")
            if analysis['duration_minutes'] > 120:
                analysis['warnings'].append("Long scraping duration")
            
        except Exception as e:
            analysis['warnings'].append(f"Error reading report: {e}")
        
        return analysis
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        return {
            'timestamp': datetime.now().isoformat(),
            'process_status': self.check_scraper_process(),
            'recent_activity': self.check_recent_activity(),
            'database': self.check_database_connection(),
            'disk_space': self.check_disk_space(),
            'latest_report': self.analyze_latest_report()
        }
    
    def save_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Save an alert to the alerts file"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        
        alerts = []
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file) as f:
                    alerts = json.load(f)
            except:
                alerts = []
        
        alerts.append(alert)
        
        # Keep only last 100 alerts
        alerts = alerts[-100:]
        
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)
    
    def check_health_and_alert(self):
        """Check health and generate alerts if needed"""
        health = self.get_system_health()
        
        # Check for issues and generate alerts
        db_status = health['database']
        if not db_status['connected']:
            self.save_alert(
                'database_connection',
                f"Database connection failed: {db_status.get('error', 'Unknown error')}",
                'critical'
            )
        
        disk_status = health['disk_space']
        if disk_status.get('warning'):
            self.save_alert(
                'disk_space',
                f"Disk usage high: {disk_status['usage_percent']:.1f}%",
                'warning'
            )
        
        activity = health['recent_activity']
        if not activity['recent_logs'] and not activity['recent_reports']:
            self.save_alert(
                'no_activity',
                "No recent scraping activity detected",
                'warning'
            )
        
        report_analysis = health['latest_report']
        for warning in report_analysis.get('warnings', []):
            self.save_alert(
                'scraping_performance',
                warning,
                'warning'
            )
        
        return health

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scraper Monitor")
    parser.add_argument('command', choices=['status', 'health', 'alerts', 'watch'],
                       help='Monitoring command')
    parser.add_argument('--interval', type=int, default=60,
                       help='Watch interval in seconds')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    monitor = ScraperMonitor()
    
    if args.command == 'status':
        health = monitor.get_system_health()
        
        if args.format == 'json':
            print(json.dumps(health, indent=2, default=str))
        else:
            print("=== Scraper Status ===")
            print(f"Timestamp: {health['timestamp']}")
            
            # Process status
            proc_status = health['process_status']
            print(f"\nProcess Status:")
            print(f"  Running: {'✅' if proc_status['running'] else '❌'}")
            print(f"  Processes: {len(proc_status['processes'])}")
            print(f"  Memory Usage: {proc_status['memory_usage']:.1f} MB")
            print(f"  CPU Usage: {proc_status['cpu_usage']:.1f}%")
            
            # Database status
            db_status = health['database']
            print(f"\nDatabase:")
            print(f"  Connected: {'✅' if db_status['connected'] else '❌'}")
            if db_status['response_time']:
                print(f"  Response Time: {db_status['response_time']:.3f}s")
            if db_status['error']:
                print(f"  Error: {db_status['error']}")
            
            # Recent activity
            activity = health['recent_activity']
            print(f"\nRecent Activity (24h):")
            print(f"  Logs: {'✅' if activity['recent_logs'] else '❌'} ({activity['log_count']} files)")
            print(f"  Reports: {'✅' if activity['recent_reports'] else '❌'} ({activity['report_count']} files)")
            
            # Disk space
            disk = health['disk_space']
            print(f"\nDisk Space:")
            print(f"  Usage: {disk['usage_percent']:.1f}% ({disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB)")
            print(f"  Free: {disk['free_gb']:.1f}GB")
            
            # Latest report
            report = health['latest_report']
            if report['has_report']:
                print(f"\nLatest Report:")
                print(f"  Success Rate: {report['success_rate']:.1f}%")
                print(f"  Properties: {report['properties_processed']}")
                print(f"  Duration: {report['duration_minutes']:.1f} minutes")
                print(f"  Languages: {', '.join(report['languages_processed'])}")
                if report['warnings']:
                    print(f"  Warnings: {', '.join(report['warnings'])}")
    
    elif args.command == 'health':
        health = monitor.check_health_and_alert()
        print("Health check completed. Alerts saved if any issues found.")
    
    elif args.command == 'alerts':
        if monitor.alerts_file.exists():
            with open(monitor.alerts_file) as f:
                alerts = json.load(f)
            
            if args.format == 'json':
                print(json.dumps(alerts, indent=2))
            else:
                print("=== Recent Alerts ===")
                for alert in alerts[-10:]:  # Show last 10
                    severity_icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(alert['severity'], '⚪')
                    print(f"{severity_icon} {alert['timestamp']} [{alert['type']}] {alert['message']}")
        else:
            print("No alerts found.")
    
    elif args.command == 'watch':
        print(f"Watching scraper health (interval: {args.interval}s). Press Ctrl+C to stop.")
        try:
            while True:
                health = monitor.check_health_and_alert()
                
                # Clear screen and show status
                os.system('clear')
                print(f"=== Scraper Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                
                proc_status = health['process_status']
                db_status = health['database']
                
                status_line = f"Process: {'🟢' if proc_status['running'] else '🔴'} | "
                status_line += f"DB: {'🟢' if db_status['connected'] else '🔴'} | "
                status_line += f"Memory: {proc_status['memory_usage']:.1f}MB | "
                status_line += f"CPU: {proc_status['cpu_usage']:.1f}%"
                
                print(status_line)
                
                # Show any recent warnings
                report = health['latest_report']
                if report.get('warnings'):
                    print(f"⚠️  Warnings: {', '.join(report['warnings'])}")
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

if __name__ == "__main__":
    exit(main())
