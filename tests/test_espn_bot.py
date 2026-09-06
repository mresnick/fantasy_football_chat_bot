"""Unit tests for espn_bot.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.espn.espn_bot import espn_bot, start_bot
import gamedaybot.utils.report as reports


class TestEspnBot:
    """Test suite for espn_bot function"""
    
    @pytest.fixture
    def mock_env_data(self):
        """Create mock environment data"""
        return {
            'str_limit': 1000,
            'bot_id': 'test_bot_id',
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'discord_webhook_url': 'https://discord.com/webhook/test',
            'league_id': 123456,
            'year': 2024,
            'swid': '{test-swid}',
            'espn_s2': 'test_s2_cookie',
            'top_half_scoring': 'false',
            'random_phrase': 'false',
            'discord_server_id': 'test_server_id',
            'discord_token': None,
            'broadcast_message': 'Test broadcast',
            'draft_date': '2024-09-01',
            'init_msg': 'Bot initialized'
        }
    
    @pytest.fixture
    def mock_league(self):
        """Create mock League object"""
        league = Mock()
        league.scoringPeriodId = 5
        league.current_week = 5
        league.settings = Mock()
        league.settings.matchup_periods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        league.settings.position_slot_counts = {
            'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'RB/WR/TE': 1,
            'D/ST': 1, 'K': 1, 'BE': 7, 'IR': 1, 'P': 0,
        }
        league.settings.faab = True
        return league
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_matchups(self, mock_str_limit, mock_league_class, 
                                   mock_discord, mock_slack, mock_groupme, 
                                   mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_matchups function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Test message"]
        
        # Mock the messaging bots
        mock_groupme_instance = Mock()
        mock_slack_instance = Mock()
        mock_discord_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = mock_slack_instance
        mock_discord.return_value = mock_discord_instance
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_matchups.return_value = "Matchups text"
            mock_espn.get_projected_scoreboard.return_value = "Projected text"
            
            espn_bot("get_matchups")
            
            mock_espn.get_matchups.assert_called_once()
            mock_espn.get_projected_scoreboard.assert_called_once()
            mock_groupme_instance.send_message.assert_called()
            mock_slack_instance.send_message.assert_called()
            mock_discord_instance.send_message.assert_called()
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_scoreboard_short(self, mock_str_limit, mock_league_class,
                                           mock_discord, mock_slack, mock_groupme,
                                           mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_scoreboard_short function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Short scoreboard"]
        
        mock_groupme_instance = Mock()
        mock_slack_instance = Mock()
        mock_discord_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = mock_slack_instance
        mock_discord.return_value = mock_discord_instance
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_scoreboard_short.return_value = "Short scoreboard"
            mock_espn.get_projected_scoreboard.return_value = "Projected"
            
            espn_bot("get_scoreboard_short")
            
            mock_espn.get_scoreboard_short.assert_called_once()
            mock_espn.get_projected_scoreboard.assert_called_once()
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_power_rankings(self, mock_str_limit, mock_league_class,
                                         mock_discord, mock_slack, mock_groupme,
                                         mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_power_rankings function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Power rankings"]
        
        mock_groupme_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_power_rankings.return_value = "Power rankings text"
            
            espn_bot("get_power_rankings")
            
            mock_espn.get_power_rankings.assert_called_once_with(mock_league)
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_trophies(self, mock_str_limit, mock_league_class,
                                   mock_discord, mock_slack, mock_groupme,
                                   mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_trophies function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Trophies text"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            # Trophies are built from structured pairs now, so the same content
            # can render as text for GroupMe/Slack and as embed fields for Discord.
            mock_espn.last_completed_week.return_value = 4
            mock_espn.trophy_fields.return_value = [
                ('👑 High score 👑', 'Alpha with 120.00 points')]

            espn_bot("get_trophies")

            mock_espn.trophy_fields.assert_called_once_with(mock_league, week=4)
            sent = mock_str_limit.call_args[0][0]
            assert 'Trophies of the week:' in sent
            assert 'Alpha with 120.00 points' in sent
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_standings(self, mock_str_limit, mock_league_class,
                                    mock_discord, mock_slack, mock_groupme,
                                    mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_standings function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Standings text"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_standings.return_value = "Standings text"
            
            espn_bot("get_standings")
            
            mock_espn.get_standings.assert_called_once_with(mock_league, False)
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_final(self, mock_str_limit, mock_league_class,
                                mock_discord, mock_slack, mock_groupme,
                                mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_final function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Final scores"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_scoreboard_short.return_value = "Score Update\n AA 120.00 -  98.00 BB"
            mock_espn.trophy_fields.return_value = [('Trophy', 'Winner')]
            # scoringPeriodId is 5, so week 4 is the one that just finished.
            mock_espn.last_completed_week.return_value = 4

            espn_bot("get_final")

            mock_espn.get_scoreboard_short.assert_called_once_with(mock_league, week=4)
            mock_espn.trophy_fields.assert_called_once_with(mock_league, week=4)
            sent = mock_str_limit.call_args[0][0]
            assert 'Week 4' in sent
            # The scoreboard's own header is dropped; the title replaces it.
            assert 'Score Update' not in sent
            assert 'AA 120.00' in sent
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_get_waiver_report(self, mock_str_limit, mock_league_class,
                                        mock_discord, mock_slack, mock_groupme,
                                        mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_waiver_report function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Waiver report"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_waiver_report.return_value = "Waiver report text"
            
            espn_bot("get_waiver_report")
            
            mock_espn.get_waiver_report.assert_called_once_with(mock_league, True)
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_win_matrix(self, mock_str_limit, mock_league_class,
                                 mock_discord, mock_slack, mock_groupme,
                                 mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with win_matrix function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Win matrix"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.recap') as mock_recap:
            mock_recap.win_matrix.return_value = "Win matrix text"
            
            espn_bot("win_matrix")
            
            mock_recap.win_matrix.assert_called_once_with(mock_league)
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_trophy_recap(self, mock_str_limit, mock_league_class,
                                   mock_discord, mock_slack, mock_groupme,
                                   mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with trophy_recap function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Trophy recap"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.recap') as mock_recap:
            mock_recap.trophy_recap.return_value = "Trophy recap text"
            
            espn_bot("trophy_recap")
            
            mock_recap.trophy_recap.assert_called_once_with(mock_league)
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    def test_espn_bot_missing_bot_info(self, mock_league_class, mock_discord,
                                       mock_slack, mock_groupme, mock_get_env, mock_env_data):
        """Test espn_bot raises exception when no messaging platform info provided"""
        # Modify env data to have no valid bot info
        mock_env_data['bot_id'] = '1'
        mock_env_data['slack_webhook_url'] = '1'
        mock_env_data['discord_webhook_url'] = '1'
        mock_get_env.return_value = mock_env_data
        
        with pytest.raises(Exception, match="No messaging platform info provided"):
            espn_bot("get_matchups")
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_out_of_season(self, mock_str_limit, mock_league_class,
                                    mock_discord, mock_slack, mock_groupme,
                                    mock_get_env, mock_env_data, mock_league):
        """Test espn_bot when out of season"""
        # Make league out of season
        mock_league.scoringPeriodId = 16
        mock_league.settings.matchup_periods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Test message"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        # Should return early and not call ESPN functions
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            espn_bot("get_matchups")
            
            mock_espn.get_matchups.assert_not_called()
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_init_function(self, mock_str_limit, mock_league_class,
                                    mock_discord, mock_slack, mock_groupme,
                                    mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with init function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Bot initialized"]
        
        mock_groupme_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        espn_bot("init")
        
        mock_groupme_instance.send_message.assert_called_with("Bot initialized")
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_broadcast_function(self, mock_str_limit, mock_league_class,
                                         mock_discord, mock_slack, mock_groupme,
                                         mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with broadcast function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Test broadcast"]
        
        mock_groupme_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        espn_bot("broadcast")
        
        mock_groupme_instance.send_message.assert_called_with("Test broadcast")
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_draft_reminder(self, mock_str_limit, mock_league_class,
                                     mock_discord, mock_slack, mock_groupme,
                                     mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with get_draft_reminder function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Draft reminder"]
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_draft_reminder.return_value = "Draft reminder text"
            
            espn_bot("get_draft_reminder")
            
            mock_espn.get_draft_reminder.assert_called_once_with(mock_league, '2024-09-01')
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_invalid_function(self, mock_str_limit, mock_league_class,
                                       mock_discord, mock_slack, mock_groupme,
                                       mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with invalid function"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["Something bad happened. HALP"]
        
        mock_groupme_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        espn_bot("invalid_function")
        
        mock_groupme_instance.send_message.assert_called_with("Something bad happened. HALP")
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    @patch('gamedaybot.espn.espn_bot.util.str_limit_check')
    def test_espn_bot_empty_message(self, mock_str_limit, mock_league_class,
                                    mock_discord, mock_slack, mock_groupme,
                                    mock_get_env, mock_env_data, mock_league):
        """Test espn_bot with empty message"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = mock_league
        mock_str_limit.return_value = ["", "  ", "\n"]  # Empty/whitespace messages
        
        mock_groupme_instance = Mock()
        mock_groupme.return_value = mock_groupme_instance
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_matchups.return_value = ""
            mock_espn.get_projected_scoreboard.return_value = ""
            
            espn_bot("get_matchups")
            
            # Should not send empty messages
            mock_groupme_instance.send_message.assert_not_called()
    
    def test_start_bot_function(self):
        """Test start_bot function"""
        mock_bot = Mock()
        
        start_bot(mock_bot, "test_token")
        
        mock_bot.run.assert_called_once_with("test_token")
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    def test_league_initialization_with_cookies(self, mock_league_class, mock_discord,
                                                mock_slack, mock_groupme, mock_get_env, mock_env_data):
        """Test League initialization with cookies"""
        mock_get_env.return_value = mock_env_data
        mock_league_class.return_value = Mock()
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.util.str_limit_check'):
            espn_bot("init")
            
            # Should initialize with cookies since they're provided
            mock_league_class.assert_called_once_with(
                league_id=123456,
                year=2024,
                espn_s2='test_s2_cookie',
                swid='{test-swid}'
            )
    
    @patch('gamedaybot.espn.espn_bot.get_env_vars')
    @patch('gamedaybot.espn.espn_bot.GroupMe')
    @patch('gamedaybot.espn.espn_bot.Slack')
    @patch('gamedaybot.espn.espn_bot.Discord')
    @patch('gamedaybot.espn.espn_bot.League')
    def test_league_initialization_without_cookies(self, mock_league_class, mock_discord,
                                                   mock_slack, mock_groupme, mock_get_env):
        """Test League initialization without cookies"""
        env_data_no_cookies = {
            'str_limit': 1000,
            'bot_id': 'test_bot_id',
            'league_id': 123456,
            'year': 2024,
            'swid': '{1}',  # Default value
            'espn_s2': '1',  # Default value
            'discord_token': None
        }
        mock_get_env.return_value = env_data_no_cookies
        mock_league_class.return_value = Mock()
        
        mock_groupme.return_value = Mock()
        mock_slack.return_value = Mock()
        mock_discord.return_value = Mock()
        
        with patch('gamedaybot.espn.espn_bot.util.str_limit_check'):
            espn_bot("init")
            
            # Should initialize without cookies since they're default values
            mock_league_class.assert_called_once_with(
                league_id=123456,
                year=2024
            )


class TestSeasonEndGuard:
    """The 'Not in active season' guard used to swallow the final week's recap.

    On the Tuesday after the last matchup week, scoringPeriodId has already
    advanced past len(settings.matchup_periods), so get_final never ran and the
    season's last Final message was never sent.
    """

    LAST_WEEK = 14

    @pytest.fixture
    def env_data(self):
        return {
            'str_limit': 1000,
            'bot_id': 'test_bot_id',
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'discord_webhook_url': 'https://discord.com/webhook/test',
            'league_id': 123456,
            'year': 2024,
            'swid': '{test-swid}',
            'espn_s2': 'test_s2_cookie',
            'top_half_scoring': 'false',
            'random_phrase': 'false',
            'discord_server_id': 'test_server_id',
            'discord_token': None,
            'init_msg': 'Bot initialized',
        }

    def _league(self, scoring_period_id):
        league = Mock()
        league.scoringPeriodId = scoring_period_id
        league.current_week = min(scoring_period_id, self.LAST_WEEK)
        league.settings = Mock()
        league.settings.matchup_periods = list(range(1, self.LAST_WEEK + 1))
        league.settings.faab = True
        return league

    def _run(self, function, scoring_period_id, env_data):
        """Run espn_bot and report whether anything was actually sent."""
        with patch('gamedaybot.espn.espn_bot.get_env_vars', return_value=env_data),              patch('gamedaybot.espn.espn_bot.GroupMe'),              patch('gamedaybot.espn.espn_bot.Slack'),              patch('gamedaybot.espn.espn_bot.Discord'),              patch('gamedaybot.espn.espn_bot.League',
                   return_value=self._league(scoring_period_id)),              patch('gamedaybot.espn.espn_bot.util.str_limit_check',
                   return_value=["msg"]) as mock_limit,              patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_scoreboard_short.return_value = "scores"
            mock_espn.get_trophies.return_value = "trophies"
            mock_espn.get_power_rankings.return_value = "rankings"
            mock_espn.get_standings.return_value = "standings"
            mock_espn.get_matchups.return_value = "matchups"
            mock_espn.get_projected_scoreboard.return_value = "projected"
            mock_espn.last_completed_week.return_value = self.LAST_WEEK
            espn_bot(function)
            return mock_limit.called

    def test_get_final_still_sends_on_tuesday_after_the_final_week(self, env_data):
        # scoringPeriodId has rolled to 15, one past the last matchup week.
        assert self._run("get_final", self.LAST_WEEK + 1, env_data) is True

    def test_other_end_of_season_recaps_still_send(self, env_data):
        for function in ("get_power_rankings", "get_standings", "get_trophies"):
            assert self._run(function, self.LAST_WEEK + 1, env_data) is True, function

    def test_recaps_stop_once_the_grace_week_has_passed(self, env_data):
        assert self._run("get_final", self.LAST_WEEK + 2, env_data) is False

    def test_in_season_functions_stop_at_the_final_week(self, env_data):
        # get_matchups has no week to report once the season is over.
        assert self._run("get_matchups", self.LAST_WEEK + 1, env_data) is False
        assert self._run("get_matchups", self.LAST_WEEK, env_data) is True


class TestEmbedSendPath:
    """
    Discord receives a rich embed; GroupMe and Slack receive the text they always did.

    The bot builds one Report and renders it per platform, so this pins that the
    text platforms were not changed by the embed work.
    """

    LAST_WEEK = 14

    @pytest.fixture
    def env_data(self):
        return {
            'str_limit': 1000,
            'bot_id': 'test_bot_id',
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'discord_webhook_url': 'https://discord.com/webhook/test',
            'league_id': 123456,
            'year': 2024,
            'swid': '{test-swid}',
            'espn_s2': 'test_s2_cookie',
            'top_half_scoring': 'false',
            'random_phrase': 'false',
            'discord_server_id': 'test_server_id',
            'discord_token': None,
        }

    def _league(self):
        league = Mock()
        league.scoringPeriodId = 10
        league.current_week = 10
        league.settings = Mock()
        league.settings.matchup_periods = list(range(1, self.LAST_WEEK + 1))
        return league

    def _run(self, function, env_data, standings_text="Current Standings\n 1: AA (5-2)"):
        """Run the bot and return the three platform mocks."""
        groupme, slack, discord_hook = Mock(), Mock(), Mock()
        with patch('gamedaybot.espn.espn_bot.get_env_vars', return_value=env_data), \
             patch('gamedaybot.espn.espn_bot.GroupMe', return_value=groupme), \
             patch('gamedaybot.espn.espn_bot.Slack', return_value=slack), \
             patch('gamedaybot.espn.espn_bot.Discord', return_value=discord_hook), \
             patch('gamedaybot.espn.espn_bot.League', return_value=self._league()), \
             patch('gamedaybot.espn.espn_bot.espn') as mock_espn:
            mock_espn.get_standings.return_value = standings_text
            espn_bot(function)
        return groupme, slack, discord_hook

    def test_discord_gets_an_embed(self, env_data):
        _, _, discord_hook = self._run('get_standings', env_data)

        discord_hook.send_message.assert_called_once()
        kwargs = discord_hook.send_message.call_args[1]
        assert 'embed' in kwargs
        assert kwargs['embed']['title'] == 'Current Standings'

    def test_text_platforms_get_the_unchanged_text(self, env_data):
        groupme, slack, _ = self._run('get_standings', env_data)

        for platform in (groupme, slack):
            platform.send_message.assert_called_once()
            sent = platform.send_message.call_args[0][0]
            assert sent == "Current Standings\n 1: AA (5-2)"
            # No embed keyword reaches the text platforms.
            assert platform.send_message.call_args[1] == {}

    def test_embed_is_coloured_per_function(self, env_data):
        _, _, discord_hook = self._run('get_standings', env_data)
        assert discord_hook.send_message.call_args[1]['embed']['color'] == reports.BLUE

    def test_oversized_report_falls_back_to_text_on_discord(self, env_data):
        # Too large for one embed, so Discord gets the same split text as the
        # others rather than a silently truncated card.
        huge = "Current Standings\n" + ("x" * 200 + "\n") * 40
        _, _, discord_hook = self._run('get_standings', env_data, standings_text=huge)

        assert discord_hook.send_message.call_count > 1
        for call in discord_hook.send_message.call_args_list:
            assert 'embed' not in call[1]
            assert isinstance(call[0][0], str)

    def test_nothing_is_sent_for_an_empty_report(self, env_data):
        groupme, slack, discord_hook = self._run('get_standings', env_data, standings_text='')

        groupme.send_message.assert_not_called()
        slack.send_message.assert_not_called()
        discord_hook.send_message.assert_not_called()
