"""Unit tests for env_vars.py"""
import pytest
from unittest.mock import patch, Mock
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.espn.env_vars import get_env_vars


class TestEnvVars:
    """Test suite for env_vars module"""
    
    @pytest.fixture
    def full_env_vars(self):
        """Complete set of environment variables"""
        return {
            'START_DATE': '2024-09-01',
            'END_DATE': '2024-12-31',
            'TIMEZONE': 'America/Chicago',
            'DAILY_WAIVER': 'true',
            'MONITOR_REPORT': 'false',
            'BOT_ID': 'test_bot_id_123',
            'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            'DISCORD_WEBHOOK_URL': 'https://discord.com/webhook/test',
            'LEAGUE_ID': '123456',
            'LEAGUE_YEAR': '2024',
            'SWID': 'test-swid-123',
            'ESPN_S2': 'test_espn_s2_cookie',
            'TEST': 'false',
            'TOP_HALF_SCORING': 'true',
            'RANDOM_PHRASE': 'true',
            'WAIVER_REPORT': 'true',
            'INIT_MSG': 'Bot initialized successfully!',
            'DISCORD_TOKEN': 'discord_token_123',
            'DISCORD_SERVER_ID': 'server_123',
            'DRAFT_DATE': '2024-08-25'
        }
    
    @pytest.fixture
    def minimal_env_vars(self):
        """Minimal required environment variables"""
        return {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id'
        }
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_env_vars_all_defaults(self):
        """Test get_env_vars with no environment variables (all defaults)"""
        # Set only the required LEAGUE_ID and one messaging platform
        with patch.dict(os.environ, {'LEAGUE_ID': '123456', 'BOT_ID': 'test_bot'}):
            result = get_env_vars()
            
            # Check default values
            assert result['ff_start_date'] == '2024-09-05'
            assert result['ff_end_date'] == '2024-12-31'
            assert result['my_timezone'] == 'America/New_York'
            assert result['daily_waiver'] is False
            assert result['monitor_report'] is True
            assert result['year'] == 2024
            assert result['swid'] == '{1}'
            assert result['espn_s2'] == '1'
            assert result['test'] is False
            assert result['top_half_scoring'] is False
            assert result['random_phrase'] is False
            assert result['waiver_report'] is False
            assert result['discord_token'] is None
            assert result['discord_server_id'] is None
            assert result['draft_date'] is None
    
    def test_get_env_vars_with_full_config(self, full_env_vars):
        """Test get_env_vars with all environment variables set"""
        with patch.dict(os.environ, full_env_vars, clear=True):
            result = get_env_vars()
            
            # Check all values are set correctly
            assert result['ff_start_date'] == '2024-09-01'
            assert result['ff_end_date'] == '2024-12-31'
            assert result['my_timezone'] == 'America/Chicago'
            assert result['daily_waiver'] is True
            assert result['monitor_report'] is False
            assert result['bot_id'] == 'test_bot_id_123'
            assert result['slack_webhook_url'] == 'https://hooks.slack.com/test'
            assert result['discord_webhook_url'] == 'https://discord.com/webhook/test'
            assert result['league_id'] == '123456'
            assert result['year'] == 2024
            assert result['swid'] == '{test-swid-123}'
            assert result['espn_s2'] == 'test_espn_s2_cookie'
            assert result['test'] is False
            assert result['top_half_scoring'] is True
            assert result['random_phrase'] is True
            assert result['waiver_report'] is True
            assert result['init_msg'] == 'Bot initialized successfully!'
            assert result['discord_token'] == 'discord_token_123'
            assert result['discord_server_id'] == 'server_123'
            assert result['draft_date'] == '2024-08-25'
    
    def test_get_env_vars_str_limit_groupme(self):
        """Test string limit is set correctly for GroupMe"""
        env_vars = {'LEAGUE_ID': '123456', 'BOT_ID': 'test_bot_id'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # GroupMe has 1000 char limit
            assert result['str_limit'] == 1000
    
    def test_get_env_vars_str_limit_slack(self):
        """Test string limit is set correctly for Slack"""
        env_vars = {'LEAGUE_ID': '123456', 'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # Slack has 40000 char limit (default)
            assert result['str_limit'] == 40000
    
    def test_get_env_vars_str_limit_discord(self):
        """Test string limit is set correctly for Discord"""
        env_vars = {'LEAGUE_ID': '123456', 'DISCORD_WEBHOOK_URL': 'https://discord.com/webhook/test'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # Discord has 3000 char limit
            assert result['str_limit'] == 3000
    
    def test_get_env_vars_str_limit_multiple_platforms(self):
        """Test string limit when multiple platforms are configured"""
        env_vars = {
            'LEAGUE_ID': '123456', 
            'BOT_ID': 'test_bot_id',
            'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
            'DISCORD_WEBHOOK_URL': 'https://discord.com/webhook/test'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # Should prioritize Discord (3000) over GroupMe (1000) over Slack (40000)
            assert result['str_limit'] == 3000
    
    def test_get_env_vars_no_messaging_platform(self):
        """Test get_env_vars raises exception when no messaging platform is configured"""
        env_vars = {'LEAGUE_ID': '123456'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(Exception, match="No messaging platform info provided"):
                get_env_vars()
    
    def test_get_env_vars_empty_messaging_platform_values(self):
        """Test get_env_vars raises exception when messaging platform values are empty"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': '',
            'SLACK_WEBHOOK_URL': '',
            'DISCORD_WEBHOOK_URL': ''
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(Exception, match="No messaging platform info provided"):
                get_env_vars()
    
    def test_get_env_vars_missing_league_id(self):
        """Test get_env_vars raises exception when LEAGUE_ID is missing"""
        env_vars = {'BOT_ID': 'test_bot_id'}
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(KeyError):
                get_env_vars()
    
    def test_swid_formatting_no_braces(self):
        """Test SWID formatting when braces are missing"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'SWID': 'test-swid-without-braces'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['swid'] == '{test-swid-without-braces}'
    
    def test_swid_formatting_partial_braces(self):
        """Test SWID formatting when only one brace is present"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'SWID': '{test-swid-missing-end'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['swid'] == '{test-swid-missing-end}'
    
    def test_swid_formatting_already_formatted(self):
        """Test SWID formatting when already properly formatted"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'SWID': '{already-formatted-swid}'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['swid'] == '{already-formatted-swid}'
    
    @patch('gamedaybot.espn.env_vars.utils.str_to_bool')
    def test_boolean_environment_variables(self, mock_str_to_bool):
        """Test that boolean environment variables are processed correctly"""
        mock_str_to_bool.side_effect = lambda x: x.lower() == 'true'
        
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'DAILY_WAIVER': 'true',
            'MONITOR_REPORT': 'false',
            'TEST': 'true',
            'TOP_HALF_SCORING': 'false',
            'RANDOM_PHRASE': 'true',
            'WAIVER_REPORT': 'false'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # Verify str_to_bool was called for each boolean variable
            assert mock_str_to_bool.call_count == 6
            
            # Verify boolean values are set correctly
            assert result['daily_waiver'] is True
            assert result['monitor_report'] is False
            assert result['test'] is True
            assert result['top_half_scoring'] is False
            assert result['random_phrase'] is True
            assert result['waiver_report'] is False
    
    def test_league_year_conversion(self):
        """Test LEAGUE_YEAR is converted to integer"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'LEAGUE_YEAR': '2023'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['year'] == 2023
            assert isinstance(result['year'], int)
    
    def test_league_year_invalid_format(self):
        """Test get_env_vars handles invalid LEAGUE_YEAR format"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'LEAGUE_YEAR': 'not_a_number'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError):
                get_env_vars()
    
    def test_optional_discord_fields(self):
        """Test optional Discord-related fields"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'DISCORD_TOKEN': 'token_123',
            'DISCORD_SERVER_ID': 'server_456'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['discord_token'] == 'token_123'
            assert result['discord_server_id'] == 'server_456'
    
    def test_optional_init_message(self):
        """Test optional initialization message"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'INIT_MSG': 'Custom initialization message!'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['init_msg'] == 'Custom initialization message!'
    
    def test_missing_optional_init_message(self):
        """Test behavior when INIT_MSG is not provided"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # Should not have init_msg key when not provided
            assert 'init_msg' not in result
    
    def test_draft_date_configuration(self):
        """Test draft date configuration"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'DRAFT_DATE': '2024-08-30'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            assert result['draft_date'] == '2024-08-30'
    
    def test_timezone_variations(self):
        """Test various timezone configurations"""
        timezones = [
            'America/New_York',
            'America/Chicago', 
            'America/Los_Angeles',
            'Europe/London',
            'UTC'
        ]
        
        for timezone in timezones:
            env_vars = {
                'LEAGUE_ID': '123456',
                'BOT_ID': 'test_bot_id',
                'TIMEZONE': timezone
            }
            
            with patch.dict(os.environ, env_vars, clear=True):
                result = get_env_vars()
                
                assert result['my_timezone'] == timezone
    
    def test_date_format_variations(self):
        """Test various date format inputs"""
        dates = [
            ('2024-09-01', '2024-12-31'),
            ('2023-08-15', '2024-01-15'),
            ('2025-01-01', '2025-12-31')
        ]
        
        for start_date, end_date in dates:
            env_vars = {
                'LEAGUE_ID': '123456',
                'BOT_ID': 'test_bot_id',
                'START_DATE': start_date,
                'END_DATE': end_date
            }
            
            with patch.dict(os.environ, env_vars, clear=True):
                result = get_env_vars()
                
                assert result['ff_start_date'] == start_date
                assert result['ff_end_date'] == end_date
    
    def test_environment_variable_case_sensitivity(self):
        """Test that environment variable names are case-sensitive"""
        env_vars = {
            'LEAGUE_ID': '123456',
            'BOT_ID': 'test_bot_id',
            'timezone': 'America/Chicago',  # lowercase should be ignored
            'TIMEZONE': 'America/New_York'  # uppercase should be used
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            result = get_env_vars()
            
            # Should use the uppercase version
            assert result['my_timezone'] == 'America/New_York'
    
    def test_comprehensive_data_structure(self, full_env_vars):
        """Test that returned data structure contains all expected keys"""
        with patch.dict(os.environ, full_env_vars, clear=True):
            result = get_env_vars()
            
            expected_keys = [
                'ff_start_date', 'ff_end_date', 'my_timezone', 'daily_waiver',
                'monitor_report', 'str_limit', 'bot_id', 'slack_webhook_url',
                'discord_webhook_url', 'league_id', 'year', 'swid', 'espn_s2',
                'test', 'top_half_scoring', 'random_phrase', 'waiver_report',
                'init_msg', 'discord_token', 'discord_server_id', 'draft_date'
            ]
            
            for key in expected_keys:
                assert key in result
    
    def test_minimal_configuration_data_structure(self, minimal_env_vars):
        """Test data structure with minimal configuration"""
        with patch.dict(os.environ, minimal_env_vars, clear=True):
            result = get_env_vars()
            
            # Required keys should always be present
            required_keys = [
                'ff_start_date', 'ff_end_date', 'my_timezone', 'daily_waiver',
                'monitor_report', 'str_limit', 'bot_id', 'slack_webhook_url',
                'discord_webhook_url', 'league_id', 'year', 'swid', 'espn_s2',
                'test', 'top_half_scoring', 'random_phrase', 'waiver_report',
                'discord_token', 'discord_server_id', 'draft_date'
            ]
            
            for key in required_keys:
                assert key in result
            
            # init_msg should not be present when not configured
            assert 'init_msg' not in result