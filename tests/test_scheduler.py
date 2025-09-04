"""Unit tests for scheduler.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.espn.scheduler import scheduler


class TestScheduler:
    """Test suite for scheduler module"""
    
    @pytest.fixture
    def mock_env_data(self):
        """Create mock environment data"""
        return {
            'ff_start_date': '2024-09-01',
            'ff_end_date': '2025-01-31',
            'my_timezone': 'America/Chicago',
            'daily_waiver': False,
            'monitor_report': False,
            'draft_date': None
        }
    
    @pytest.fixture
    def mock_env_data_with_options(self):
        """Create mock environment data with optional features enabled"""
        return {
            'ff_start_date': '2024-09-01',
            'ff_end_date': '2025-01-31',
            'my_timezone': 'America/Chicago',
            'daily_waiver': True,
            'monitor_report': True,
            'draft_date': '2024-08-25'
        }
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('builtins.print')
    def test_scheduler_basic_setup(self, mock_print, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test basic scheduler setup with minimal configuration"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Verify scheduler was created with correct settings
        mock_scheduler_class.assert_called_once_with(job_defaults={'misfire_grace_time': 15 * 60})
        
        # Verify basic jobs were added
        assert mock_scheduler_instance.add_job.call_count >= 7  # At least 7 basic jobs
        
        # Verify scheduler was started
        mock_scheduler_instance.start.assert_called_once()
        mock_print.assert_called_with("Ready!")
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_close_scores_job(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test close scores job scheduling"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find the close scores job call
        close_scores_call = None
        for call in mock_scheduler_instance.add_job.call_args_list:
            if call[1].get('id') == 'close_scores':
                close_scores_call = call
                break
        
        assert close_scores_call is not None
        assert close_scores_call[0][0] == mock_espn_bot  # Function
        assert close_scores_call[0][1] == 'cron'  # Trigger type
        assert close_scores_call[0][2] == ['get_close_scores']  # Arguments
        assert close_scores_call[1]['day_of_week'] == 'mon'
        assert close_scores_call[1]['hour'] == 18
        assert close_scores_call[1]['minute'] == 30
        assert close_scores_call[1]['timezone'] == 'America/New_York'
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_power_rankings_job(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test power rankings job scheduling"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find the power rankings job call
        power_rankings_call = None
        for call in mock_scheduler_instance.add_job.call_args_list:
            if call[1].get('id') == 'power_rankings':
                power_rankings_call = call
                break
        
        assert power_rankings_call is not None
        assert power_rankings_call[0][2] == ['get_power_rankings']
        assert power_rankings_call[1]['day_of_week'] == 'tue'
        assert power_rankings_call[1]['hour'] == 18
        assert power_rankings_call[1]['minute'] == 30
        assert power_rankings_call[1]['timezone'] == mock_env_data['my_timezone']
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_final_job(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test final scores job scheduling"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find the final job call
        final_call = None
        for call in mock_scheduler_instance.add_job.call_args_list:
            if call[1].get('id') == 'final':
                final_call = call
                break
        
        assert final_call is not None
        assert final_call[0][2] == ['get_final']
        assert final_call[1]['day_of_week'] == 'tue'
        assert final_call[1]['hour'] == 9
        assert final_call[1]['minute'] == 45
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_standings_job(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test standings job scheduling"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find the standings job call
        standings_call = None
        for call in mock_scheduler_instance.add_job.call_args_list:
            if call[1].get('id') == 'standings':
                standings_call = call
                break
        
        assert standings_call is not None
        assert standings_call[0][2] == ['get_standings']
        assert standings_call[1]['day_of_week'] == 'wed'
        assert standings_call[1]['hour'] == 7
        assert standings_call[1]['minute'] == 30
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_waiver_report_basic(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test basic waiver report job scheduling (Wednesday only)"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find waiver report job calls
        waiver_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                       if call[1].get('id') == 'waiver_report']
        
        # Should have exactly one waiver report job (Wednesday only)
        assert len(waiver_calls) == 1
        waiver_call = waiver_calls[0]
        assert waiver_call[0][2] == ['get_waiver_report']
        assert waiver_call[1]['day_of_week'] == 'wed'
        assert waiver_call[1]['hour'] == 7
        assert waiver_call[1]['minute'] == 31
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_daily_waiver_enabled(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data_with_options):
        """Test daily waiver report when enabled"""
        mock_get_env.return_value = mock_env_data_with_options
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find waiver report job calls
        waiver_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                       if call[1].get('id') == 'waiver_report']
        
        # Should have daily waiver report job (replaces Wednesday-only)
        daily_waiver_call = None
        for call in waiver_calls:
            if 'mon, tue, thu, fri, sat, sun' in call[1].get('day_of_week', ''):
                daily_waiver_call = call
                break
        
        assert daily_waiver_call is not None
        assert daily_waiver_call[1]['hour'] == 7
        assert daily_waiver_call[1]['minute'] == 31
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_matchups_job(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test matchups job scheduling"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find the matchups job call
        matchups_call = None
        for call in mock_scheduler_instance.add_job.call_args_list:
            if call[1].get('id') == 'matchups':
                matchups_call = call
                break
        
        assert matchups_call is not None
        assert matchups_call[0][2] == ['get_matchups']
        assert matchups_call[1]['day_of_week'] == 'thu'
        assert matchups_call[1]['hour'] == 19
        assert matchups_call[1]['minute'] == 30
        assert matchups_call[1]['timezone'] == 'America/New_York'
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_scoreboard_jobs(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test scoreboard job scheduling"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find scoreboard job calls
        scoreboard_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                           if 'scoreboard' in call[1].get('id', '')]
        
        # Should have two scoreboard jobs
        assert len(scoreboard_calls) >= 2
        
        # Find scoreboard1 (Friday/Monday)
        scoreboard1_call = None
        for call in scoreboard_calls:
            if call[1].get('id') == 'scoreboard1':
                scoreboard1_call = call
                break
        
        assert scoreboard1_call is not None
        assert scoreboard1_call[0][2] == ['get_scoreboard_short']
        assert scoreboard1_call[1]['day_of_week'] == 'fri,mon'
        assert scoreboard1_call[1]['hour'] == 7
        assert scoreboard1_call[1]['minute'] == 30
        
        # Find scoreboard2 (Sunday)
        scoreboard2_call = None
        for call in scoreboard_calls:
            if call[1].get('id') == 'scoreboard2':
                scoreboard2_call = call
                break
        
        assert scoreboard2_call is not None
        assert scoreboard2_call[0][2] == ['get_scoreboard_short']
        assert scoreboard2_call[1]['day_of_week'] == 'sun'
        assert scoreboard2_call[1]['hour'] == '16,20'
        assert scoreboard2_call[1]['timezone'] == 'America/New_York'
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_monitor_report_disabled(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that monitor report is not scheduled when disabled"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find monitor job calls
        monitor_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                        if call[1].get('id') == 'monitor']
        
        # Should have no monitor jobs when disabled
        assert len(monitor_calls) == 0
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_monitor_report_enabled(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data_with_options):
        """Test monitor report job when enabled"""
        mock_get_env.return_value = mock_env_data_with_options
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find monitor job calls
        monitor_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                        if call[1].get('id') == 'monitor']
        
        # Should have one monitor job when enabled
        assert len(monitor_calls) == 1
        monitor_call = monitor_calls[0]
        assert monitor_call[0][2] == ['get_monitor']
        assert monitor_call[1]['day_of_week'] == 'thu, sun, mon'
        assert monitor_call[1]['hour'] == 7
        assert monitor_call[1]['minute'] == 30
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_draft_reminder_disabled(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that draft reminder is not scheduled when draft_date not provided"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find draft reminder job calls
        draft_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                      if call[1].get('id') == 'draft_reminder']
        
        # Should have no draft reminder jobs when draft_date is None
        assert len(draft_calls) == 0
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    @patch('gamedaybot.espn.scheduler.espn_bot')
    def test_scheduler_draft_reminder_enabled(self, mock_espn_bot, mock_get_env, mock_scheduler_class, mock_env_data_with_options):
        """Test draft reminder job when draft_date is provided"""
        mock_get_env.return_value = mock_env_data_with_options
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Find draft reminder job calls
        draft_calls = [call for call in mock_scheduler_instance.add_job.call_args_list 
                      if call[1].get('id') == 'draft_reminder']
        
        # Should have one draft reminder job when enabled
        assert len(draft_calls) == 1
        draft_call = draft_calls[0]
        assert draft_call[0][2] == ['get_draft_reminder']
        assert draft_call[1]['hour'] == 9
        assert draft_call[1]['minute'] == 0
        assert draft_call[1]['timezone'] == mock_env_data_with_options['my_timezone']
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_date_range_configuration(self, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that jobs are configured with correct date ranges"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Check that all jobs have start_date and end_date configured
        for call in mock_scheduler_instance.add_job.call_args_list:
            if call[1].get('id') != 'draft_reminder':  # Draft reminder doesn't have date range
                assert call[1]['start_date'] == mock_env_data['ff_start_date']
                assert call[1]['end_date'] == mock_env_data['ff_end_date']
            assert call[1]['replace_existing'] is True
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_timezone_configuration(self, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that jobs are configured with correct timezones"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Jobs that should use game timezone (America/New_York)
        game_timezone_jobs = ['close_scores', 'matchups', 'scoreboard2']
        
        # Jobs that should use local timezone
        local_timezone_jobs = ['power_rankings', 'final', 'standings', 'waiver_report', 
                              'scoreboard1', 'monitor', 'draft_reminder']
        
        for call in mock_scheduler_instance.add_job.call_args_list:
            job_id = call[1].get('id', '')
            
            if job_id in game_timezone_jobs:
                assert call[1]['timezone'] == 'America/New_York'
            elif job_id in local_timezone_jobs:
                expected_timezone = mock_env_data['my_timezone']
                if call[1].get('timezone'):  # Some jobs might not have timezone set
                    assert call[1]['timezone'] == expected_timezone
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_job_count(self, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that correct number of jobs are scheduled with minimal config"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # With minimal config, should have these jobs:
        # 1. close_scores, 2. power_rankings, 3. final, 4. standings, 
        # 5. waiver_report, 6. matchups, 7. scoreboard1, 8. scoreboard2
        # Total: 8 jobs
        expected_jobs = 8
        assert mock_scheduler_instance.add_job.call_count == expected_jobs
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_job_count_with_options(self, mock_get_env, mock_scheduler_class, mock_env_data_with_options):
        """Test that correct number of jobs are scheduled with all options enabled"""
        mock_get_env.return_value = mock_env_data_with_options
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # With all options enabled, should have additional jobs:
        # Basic 8 jobs + monitor (1) + draft_reminder (1) + daily_waiver replaces weekly waiver
        # Total: 10 jobs (8 basic - 1 weekly waiver + 1 daily waiver + 1 monitor + 1 draft)
        # With all options enabled, we get:
        # 8 basic jobs + 1 monitor + 1 draft_reminder = 10 jobs
        # (daily waiver replaces weekly waiver with same ID)
        # But add_job is called 11 times total because both waiver jobs are added
        # even though the second one replaces the first
        expected_jobs = 11
        assert mock_scheduler_instance.add_job.call_count == expected_jobs
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_misfire_grace_time(self, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that scheduler is configured with correct misfire grace time"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # Verify scheduler was created with 15-minute misfire grace time
        expected_job_defaults = {'misfire_grace_time': 15 * 60}
        mock_scheduler_class.assert_called_once_with(job_defaults=expected_job_defaults)
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_replace_existing_jobs(self, mock_get_env, mock_scheduler_class, mock_env_data):
        """Test that all jobs are configured to replace existing ones"""
        mock_get_env.return_value = mock_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        scheduler()
        
        # All jobs should have replace_existing=True
        for call in mock_scheduler_instance.add_job.call_args_list:
            assert call[1]['replace_existing'] is True
    
    @patch('gamedaybot.espn.scheduler.BlockingScheduler')
    @patch('gamedaybot.espn.scheduler.get_env_vars')
    def test_scheduler_error_handling(self, mock_get_env, mock_scheduler_class):
        """Test scheduler behavior when environment data is missing"""
        # Test with missing keys
        incomplete_env_data = {
            'ff_start_date': '2024-09-01',
            # Missing other required keys
        }
        mock_get_env.return_value = incomplete_env_data
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance
        
        # Should raise KeyError for missing required environment variables
        with pytest.raises(KeyError):
            scheduler()