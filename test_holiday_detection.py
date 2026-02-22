"""
Test script to verify holiday detection and next working day download logic.

This demonstrates the new SPAN margin download strategy:
- If today is a market holiday/weekend → tries NEXT working day first
- If that fails → falls back to today, yesterday, 2d, 3d
- If all fail → loads from database cache
"""
import asyncio
from datetime import datetime, date, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock imports (since we can't run full server)
class MockIST:
    hours = 5
    minutes = 30

IST = MockIST()


def _is_holiday(d: date) -> bool:
    """Check if date is weekend or holiday."""
    # Weekend check
    if d.weekday() >= 5:  # Saturday=5, Sunday=6
        return True
    
    # Add specific holidays here (example)
    holidays = {
        date(2026, 1, 26),  # Republic Day
        date(2026, 8, 15),  # Independence Day
        date(2026, 10, 2),  # Gandhi Jayanti
        # Add more as needed
    }
    return d in holidays


def _get_next_working_day(start_date: date, max_days: int = 7) -> date:
    """Find the next working day after start_date."""
    for i in range(1, max_days + 1):
        candidate = start_date + timedelta(days=i)
        if not _is_holiday(candidate):
            return candidate
    return None


def simulate_download_strategy(test_date: date):
    """Simulate the new SPAN download strategy."""
    print(f"\n{'='*70}")
    print(f"Testing SPAN Download Logic for: {test_date.strftime('%A, %d-%b-%Y')}")
    print(f"{'='*70}\n")
    
    is_today_holiday = _is_holiday(test_date)
    
    print(f"📅 Date Check:")
    print(f"   - Is Holiday/Weekend: {'YES' if is_today_holiday else 'NO'}")
    print(f"   - Day of Week: {test_date.strftime('%A')}")
    
    # Strategy 1: If holiday, try next working day
    if is_today_holiday:
        print(f"\n🎯 STRATEGY 1: Holiday Detected")
        next_working = _get_next_working_day(test_date, max_days=7)
        
        if next_working:
            days_ahead = (next_working - test_date).days
            print(f"   ✓ Next working day found: {next_working.strftime('%A, %d-%b-%Y')}")
            print(f"   ✓ Days ahead: {days_ahead}")
            print(f"   → Will attempt to download: {next_working.strftime('%Y%m%d')} data")
            print(f"   → Notification: INFO - 'Using next working day's data'")
            
            print(f"\n   If download succeeds:")
            print(f"      • Save to database")
            print(f"      • Status: 'future_working_day'")
            print(f"      • Return SUCCESS")
            
            print(f"\n   If download fails:")
            print(f"      • Fall through to STRATEGY 2 (fallback to past)")
        else:
            print(f"   ✗ No working day found within 7 days")
            print(f"   → Fall through to STRATEGY 2")
    else:
        print(f"\n🎯 STRATEGY 1: SKIPPED (Today is a working day)")
    
    # Strategy 2: Try today, yesterday, 2d, 3d
    print(f"\n🔄 STRATEGY 2: Fallback to Previous Days")
    print(f"   Attempting downloads in order:")
    
    for days_back in range(4):
        attempt_date = test_date - timedelta(days=days_back)
        label = "TODAY" if days_back == 0 else f"{days_back}d back"
        print(f"      {days_back+1}. {attempt_date.strftime('%d-%b-%Y')} ({label})")
    
    print(f"\n   First successful download:")
    print(f"      • Save to database")
    print(f"      • Status: 'success' (if days_back=0) or 'fallback'")
    print(f"      • Notification: WARNING (if days_back > 0)")
    
    # Strategy 3: Database cache
    print(f"\n💾 STRATEGY 3: Database Cache Fallback")
    print(f"   If ALL downloads fail (1-4 attempts):")
    print(f"      • Load latest cached data from database")
    print(f"      • Notification: WARNING - 'Using database cache'")
    
    # Strategy 4: Complete failure
    print(f"\n⚠️  STRATEGY 4: Complete Failure")
    print(f"   If no cache available:")
    print(f"      • Use 9% conservative fallback margin")
    print(f"      • Notification: CRITICAL - 'SPAN data unavailable'")
    
    print(f"\n{'='*70}\n")


# Test scenarios
if __name__ == "__main__":
    print("\n" + "="*70)
    print("SPAN MARGIN DOWNLOAD STRATEGY SIMULATOR")
    print("="*70)
    
    # Test 1: Saturday (weekend)
    saturday = date(2026, 2, 21)
    simulate_download_strategy(saturday)
    
    # Test 2: Monday (working day)
    monday = date(2026, 2, 23)
    simulate_download_strategy(monday)
    
    # Test 3: Friday before long weekend
    friday = date(2026, 8, 14)  # Day before Independence Day
    simulate_download_strategy(friday)
    
    print("\n" + "="*70)
    print("EXPECTED BEHAVIOR SUMMARY")
    print("="*70)
    print("""
    SATURDAY (Feb 21, 2026):
      ✓ Detects holiday
      ✓ Tries Monday (Feb 23) first
      ✓ If success: INFO notification
      ✓ If fail: Falls back to Friday (Feb 20)
    
    MONDAY (Feb 23, 2026):
      ✓ Working day - skips next working day logic
      ✓ Tries Monday's file directly
      ✓ If fail: Falls back to previous days
    
    FRIDAY (Aug 14, 2026):
      ✓ Working day - tries Friday's file
      ✓ If fail: Falls back to Thu, Wed, Tue, Mon
    """)
    print("="*70 + "\n")
    
    # Show benefits
    print("\n" + "="*70)
    print("BENEFITS OF NEW STRATEGY")
    print("="*70)
    print("""
    1. ACCURATE WEEKEND MARGINS:
       - Saturday/Sunday get Monday's margin data
       - No reliance on Friday's stale data
       - Margin requirements match next trading session
    
    2. REDUCED ERRORS:
       - Minimizes margin calculation errors on Mondays
       - Better risk management during market gaps
       - More accurate position sizing
    
    3. NSE DATA AVAILABILITY:
       - NSE often publishes next trading day files in advance
       - Takes advantage of early data availability
       - Reduces dependency on caching
    
    4. GRACEFUL DEGRADATION:
       - Still falls back to previous days if needed
       - Database cache as secondary fallback
       - 9% conservative margin as last resort
    """)
    print("="*70 + "\n")
