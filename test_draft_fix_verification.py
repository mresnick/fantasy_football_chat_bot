#!/usr/bin/env python3
"""
Test script to verify the draft completion message fix works correctly.
This script tests various scenarios to ensure the draft completion message
is only sent once - the day after the draft date.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.espn.functionality import get_draft_reminder

def create_mock_league():
    """Create a mock league for testing"""
    league = Mock()
    league.current_week = 1
    league.espn_request = Mock()
    league.refresh_draft = Mock()
    league.draft = [Mock() for _ in range(120)]  # 120 picks
    league.settings = Mock()
    league.settings.name = "Test League"
    league.settings.team_count = 12
    return league

def test_draft_completion_scenarios():
    """Test various draft completion scenarios"""
    
    print("Testing Draft Completion Message Fix")
    print("=" * 50)
    
    # Test Case 1: Draft completed yesterday (should send message)
    print("\n1. Testing: Draft completed yesterday (should send completion message)")
    league = create_mock_league()
    
    yesterday = date.today() - timedelta(days=1)
    yesterday_timestamp = int(datetime.combine(yesterday, datetime.min.time()).timestamp() * 1000)
    
    league.espn_request.get_league_draft.return_value = {
        'draftDetail': {
            'drafted': True,
            'inProgress': False,
            'date': yesterday_timestamp
        }
    }
    
    with patch('gamedaybot.espn.functionality.date') as mock_date:
        mock_date.today.return_value = date.today()
        with patch('gamedaybot.espn.functionality.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
            
            result = get_draft_reminder(league)
            
            if "DRAFT COMPLETED!" in result:
                print("✅ PASS: Draft completion message sent correctly")
            else:
                print(f"❌ FAIL: Expected completion message, got: '{result}'")
    
    # Test Case 2: Draft completed 2 days ago (should NOT send message)
    print("\n2. Testing: Draft completed 2 days ago (should NOT send any message)")
    
    two_days_ago = date.today() - timedelta(days=2)
    two_days_ago_timestamp = int(datetime.combine(two_days_ago, datetime.min.time()).timestamp() * 1000)
    
    league.espn_request.get_league_draft.return_value = {
        'draftDetail': {
            'drafted': True,
            'inProgress': False,
            'date': two_days_ago_timestamp
        }
    }
    
    with patch('gamedaybot.espn.functionality.date') as mock_date:
        mock_date.today.return_value = date.today()
        with patch('gamedaybot.espn.functionality.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
            
            result = get_draft_reminder(league)
            
            if result == "":
                print("✅ PASS: No message sent for draft completed 2+ days ago")
            else:
                print(f"❌ FAIL: Expected empty string, got: '{result}'")
    
    # Test Case 3: Draft completed today (should NOT send completion message yet)
    print("\n3. Testing: Draft completed today (should NOT send completion message yet)")
    
    today = date.today()
    today_timestamp = int(datetime.combine(today, datetime.min.time()).timestamp() * 1000)
    
    league.espn_request.get_league_draft.return_value = {
        'draftDetail': {
            'drafted': True,
            'inProgress': False,
            'date': today_timestamp
        }
    }
    
    with patch('gamedaybot.espn.functionality.date') as mock_date:
        mock_date.today.return_value = date.today()
        with patch('gamedaybot.espn.functionality.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
            
            result = get_draft_reminder(league)
            
            if result == "":
                print("✅ PASS: No completion message sent on draft completion day")
            else:
                print(f"❌ FAIL: Expected empty string, got: '{result}'")
    
    # Test Case 4: Manual draft date - yesterday (should send completion message)
    print("\n4. Testing: Manual draft date - yesterday (should send completion message)")
    
    yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    with patch('gamedaybot.espn.functionality.date') as mock_date:
        mock_date.today.return_value = date.today()
        
        result = get_draft_reminder(league, yesterday_str)
        
        if "DRAFT COMPLETED!" in result:
            print("✅ PASS: Manual draft date completion message sent correctly")
        else:
            print(f"❌ FAIL: Expected completion message, got: '{result}'")
    
    # Test Case 5: Manual draft date - 2 days ago (should NOT send message)
    print("\n5. Testing: Manual draft date - 2 days ago (should NOT send any message)")
    
    two_days_ago_str = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    with patch('gamedaybot.espn.functionality.date') as mock_date:
        mock_date.today.return_value = date.today()
        
        result = get_draft_reminder(league, two_days_ago_str)
        
        if result == "":
            print("✅ PASS: No message sent for manual draft date 2+ days ago")
        else:
            print(f"❌ FAIL: Expected empty string, got: '{result}'")
    
    print("\n" + "=" * 50)
    print("Test completed. Review results above.")

if __name__ == "__main__":
    test_draft_completion_scenarios()