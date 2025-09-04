#!/usr/bin/env python3
"""
Test script to verify the draft reminder fix works correctly.
This tests that the draft completed message is only sent once and not repeatedly.
"""

import sys
import os
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

# Import the function we want to test
from gamedaybot.espn.functionality import get_draft_reminder


def test_draft_completed_no_repeat_messages():
    """Test that draft completed messages are not sent repeatedly."""
    print("Testing draft completed message behavior...")
    
    # Create a mock league object
    mock_league = Mock()
    mock_league.current_week = 2  # Season has started
    
    # Mock ESPN request and draft data
    mock_espn_request = Mock()
    mock_league.espn_request = mock_espn_request
    
    # Mock draft data indicating draft is completed
    yesterday_timestamp = int((datetime.now().timestamp() - 86400) * 1000)  # Draft was yesterday
    mock_draft_data = {
        'draftDetail': {
            'drafted': True,
            'inProgress': False,
            'date': yesterday_timestamp
        }
    }
    mock_espn_request.get_league_draft.return_value = mock_draft_data
    
    # Mock league.draft
    mock_league.draft = [Mock() for _ in range(120)]  # 120 picks
    mock_league.settings = Mock()
    mock_league.settings.name = "Test League"
    mock_league.settings.team_count = 12
    
    # Mock refresh_draft method
    mock_league.refresh_draft = Mock()
    
    # Test: Call the function (simulating it being called today, day after draft)
    result = get_draft_reminder(mock_league)
    
    # Should return empty string (no message) since draft was completed yesterday
    assert result == "", f"Expected empty string, got: '{result}'"
    print("✅ PASS: Draft completed message not sent repeatedly")


def test_draft_completed_on_draft_day():
    """Test that draft completed message is sent on the day of completion."""
    print("Testing draft completed message on completion day...")
    
    # Create a mock league object
    mock_league = Mock()
    mock_league.current_week = 1
    
    # Mock ESPN request and draft data
    mock_espn_request = Mock()
    mock_league.espn_request = mock_espn_request
    
    # Mock draft data indicating draft is completed TODAY
    today_timestamp = int(datetime.now().timestamp() * 1000)
    mock_draft_data = {
        'draftDetail': {
            'drafted': True,
            'inProgress': False,
            'date': today_timestamp
        }
    }
    mock_espn_request.get_league_draft.return_value = mock_draft_data
    
    # Mock league.draft
    mock_league.draft = [Mock() for _ in range(120)]  # 120 picks
    mock_league.settings = Mock()
    mock_league.settings.name = "Test League"
    mock_league.settings.team_count = 12
    
    # Mock refresh_draft method
    mock_league.refresh_draft = Mock()
    
    # Test: Call the function (simulating it being called on draft completion day)
    result = get_draft_reminder(mock_league)
    
    # Should return the draft completed message
    assert "DRAFT COMPLETED" in result, f"Expected draft completed message, got: '{result}'"
    print("✅ PASS: Draft completed message sent on completion day")


def test_manual_draft_date_no_repeat():
    """Test manual draft date doesn't send repeated messages."""
    print("Testing manual draft date behavior...")
    
    # Create a mock league object
    mock_league = Mock()
    mock_league.current_week = 2
    
    # Mock that ESPN API call fails
    mock_league.espn_request = None
    mock_league.refresh_draft = Mock(side_effect=Exception("API unavailable"))
    
    # Test with a draft date that was 3 days ago
    draft_date_3_days_ago = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    # Should return empty string (no message)
    result = get_draft_reminder(mock_league, draft_date=draft_date_3_days_ago)
    assert result == "", f"Expected empty string for old draft date, got: '{result}'"
    print("✅ PASS: No repeated messages for old manual draft dates")


def test_manual_draft_date_yesterday():
    """Test manual draft date sends completion message only on the day after."""
    print("Testing manual draft date completion message...")
    
    # Create a mock league object
    mock_league = Mock()
    mock_league.current_week = 1
    
    # Mock that ESPN API call fails
    mock_league.espn_request = None
    mock_league.refresh_draft = Mock(side_effect=Exception("API unavailable"))
    
    # Test with a draft date that was yesterday
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Should return completion message
    result = get_draft_reminder(mock_league, draft_date=yesterday)
    assert "DRAFT COMPLETED" in result, f"Expected completion message for yesterday's draft, got: '{result}'"
    print("✅ PASS: Draft completion message sent for yesterday's manual draft date")


if __name__ == "__main__":
    print("Running draft reminder fix tests...")
    print("=" * 50)
    
    try:
        test_draft_completed_no_repeat_messages()
        test_draft_completed_on_draft_day()
        test_manual_draft_date_no_repeat()
        test_manual_draft_date_yesterday()
        
        print("=" * 50)
        print("🎉 All tests passed! The draft reminder fix is working correctly.")
        print("✅ Draft completed messages will no longer be sent repeatedly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)