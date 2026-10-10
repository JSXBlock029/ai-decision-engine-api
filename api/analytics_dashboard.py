"""
API Analytics Dashboard
View API usage statistics and analytics
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.analytics import api_analytics
from datetime import datetime
import json

def print_dashboard():
    """Print analytics dashboard"""
    stats = api_analytics.get_stats(days=30)
    
    print("=" * 70)
    print(" " * 20 + "API ANALYTICS DASHBOARD")
    print("=" * 70)
    print()
    
    # Summary
    print("SUMMARY (Last 30 Days)")
    print("-" * 70)
    print(f"Total Requests:      {stats['total_requests']:,}")
    print(f"Successful:          {stats['successful_requests']:,}")
    print(f"Failed:              {stats['failed_requests']:,}")
    print(f"Success Rate:        {stats['success_rate']:.2f}%")
    print(f"Avg Response Time:   {stats['avg_response_time_ms']:.2f} ms")
    print(f"Active API Keys:     {stats['active_keys']}")
    print()
    
    # Top Endpoints
    if stats['top_endpoints']:
        print("TOP ENDPOINTS")
        print("-" * 70)
        for i, endpoint_data in enumerate(stats['top_endpoints'][:10], 1):
            endpoint = endpoint_data['endpoint']
            count = endpoint_data['count']
            print(f"{i:2}. {endpoint:40} {count:>8,} requests")
        print()
    
    # Endpoint Details
    if stats['endpoint_stats']:
        print("ENDPOINT DETAILS")
        print("-" * 70)
        for endpoint, details in list(stats['endpoint_stats'].items())[:5]:
            print(f"{endpoint}")
            print(f"  Total: {details['count']:,} | "
                  f"Success: {details['success_count']:,} | "
                  f"Errors: {details['error_count']:,} | "
                  f"Avg Time: {details['avg_response_time']:.2f} ms")
        print()
    
    # Daily Stats (last 7 days)
    daily = stats['daily_stats']
    if daily:
        print("DAILY BREAKDOWN (Last 7 Days)")
        print("-" * 70)
        sorted_days = sorted(daily.items(), reverse=True)[:7]
        for day, day_stats in sorted_days:
            print(f"{day}: {day_stats['total_requests']:,} requests "
                  f"({day_stats['successful_requests']:,} successful, "
                  f"{day_stats['failed_requests']:,} failed)")
        print()
    
    print("=" * 70)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def export_report():
    """Export analytics report"""
    report = api_analytics.export_report()
    print(f"✅ Analytics report exported to: api_analytics_report.json")
    return report

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_report()
    else:
        print_dashboard()

if __name__ == "__main__":
    main()

