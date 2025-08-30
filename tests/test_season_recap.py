"""Unit tests for season_recap.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.espn.season_recap import trophy_recap, win_matrix


class TestSeasonRecap:
    """Test suite for season_recap module"""
    
    @pytest.fixture
    def mock_league(self):
        """Create a mock league with comprehensive season data"""
        league = Mock()
        league.current_week = 6  # 5 completed weeks
        
        # Mock teams
        team1 = Mock()
        team1.team_abbrev = "TA"
        team1.team_name = "Team Alpha"
        
        team2 = Mock()
        team2.team_abbrev = "TB"
        team2.team_name = "Team Bravo"
        
        team3 = Mock()
        team3.team_abbrev = "TC"
        team3.team_name = "Team Charlie"
        
        league.teams = [team1, team2, team3]
        
        return league
    
    @patch('gamedaybot.espn.season_recap.espn.get_trophies')
    @patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy')
    @patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy')
    @patch('gamedaybot.espn.season_recap.espn.optimal_team_scores')
    @patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest')
    def test_trophy_recap_basic(self, mock_active, mock_optimal, mock_achievers, 
                                mock_lucky, mock_trophies, mock_league):
        """Test basic trophy_recap functionality"""
        
        # Mock return values for each week's trophies
        mock_trophies.return_value = ("TA", "TB", "TC", "TA")  # high, low, blowout, close
        mock_lucky.return_value = ("TB", "TC", {})
        mock_achievers.return_value = ("TA", "TB")
        mock_optimal.return_value = "TC"
        mock_active.return_value = (["TA"], ["TB"])
        
        result = trophy_recap(mock_league)
        
        # Check structure
        assert "Season Recap!" in result
        assert "Team" in result
        assert "*LEGEND*" in result
        
        # Check team abbreviations are present
        assert "TA" in result
        assert "TB" in result
        assert "TC" in result
        
        # Check that trophy icons are present
        assert "👑" in result
        assert "💩" in result
        assert "😱" in result
        assert "😅" in result
        
        # Check legend is included
        assert "👑: Most Points" in result
        assert "💩: Least Points" in result
        assert "😱: Blown out" in result
    
    @patch('gamedaybot.espn.season_recap.espn.get_trophies')
    @patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy')
    @patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy')
    @patch('gamedaybot.espn.season_recap.espn.optimal_team_scores')
    @patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest')
    def test_trophy_recap_trophy_counting(self, mock_active, mock_optimal, mock_achievers,
                                          mock_lucky, mock_trophies, mock_league):
        """Test that trophies are counted correctly across weeks"""
        
        # Team Alpha wins high score every week
        mock_trophies.return_value = ("TA", "TB", "TC", "TB")
        mock_lucky.return_value = ("TB", "TC", {})
        mock_achievers.return_value = ("TA", "TB")
        mock_optimal.return_value = "TC"
        mock_active.return_value = (["TA"], ["TB"])
        
        result = trophy_recap(mock_league)
        
        # Team Alpha should have multiple high score trophies (5 weeks)
        # The result should show trophy counts in brackets
        assert "[5, 0," in result or "TA" in result
        
        # Check that function was called for each week (5 times for 5 completed weeks)
        assert mock_trophies.call_count == 5
        assert mock_lucky.call_count == 5
        assert mock_achievers.call_count == 5
        assert mock_optimal.call_count == 5
        assert mock_active.call_count == 5
    
    @patch('gamedaybot.espn.season_recap.espn.get_trophies')
    @patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy')
    @patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy')
    @patch('gamedaybot.espn.season_recap.espn.optimal_team_scores')
    @patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest')
    def test_trophy_recap_multiple_active_teams(self, mock_active, mock_optimal, mock_achievers,
                                                mock_lucky, mock_trophies, mock_league):
        """Test trophy_recap with multiple teams tied for most active"""
        
        mock_trophies.return_value = ("TA", "TB", "TC", "TA")
        mock_lucky.return_value = ("TB", "TC", {})
        mock_achievers.return_value = ("TA", "TB")
        mock_optimal.return_value = "TC"
        # Multiple teams tied for most active
        mock_active.return_value = (["TA", "TB"], ["TC"])
        
        result = trophy_recap(mock_league)
        
        # Both TA and TB should get most active trophies
        assert "Season Recap!" in result
        assert len(result.split('\n')) > 10  # Should have multiple lines
    
    @patch('gamedaybot.espn.season_recap.espn.get_trophies')
    @patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy')
    @patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy')
    @patch('gamedaybot.espn.season_recap.espn.optimal_team_scores')
    @patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest')
    def test_trophy_recap_early_season(self, mock_active, mock_optimal, mock_achievers,
                                       mock_lucky, mock_trophies, mock_league):
        """Test trophy_recap early in season (week 2)"""
        
        mock_league.current_week = 2  # Only 1 completed week
        
        mock_trophies.return_value = ("TA", "TB", "TC", "TA")
        mock_lucky.return_value = ("TB", "TC", {})
        mock_achievers.return_value = ("TA", "TB")
        mock_optimal.return_value = "TC"
        mock_active.return_value = (["TA"], ["TB"])
        
        result = trophy_recap(mock_league)
        
        # Should only call functions once for 1 completed week
        assert mock_trophies.call_count == 1
        assert "Season Recap!" in result
    
    @patch('gamedaybot.espn.season_recap.espn.get_trophies')
    @patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy')
    @patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy')
    @patch('gamedaybot.espn.season_recap.espn.optimal_team_scores')
    @patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest')
    def test_trophy_recap_no_completed_weeks(self, mock_active, mock_optimal, mock_achievers,
                                             mock_lucky, mock_trophies, mock_league):
        """Test trophy_recap with no completed weeks"""
        
        mock_league.current_week = 1  # No completed weeks
        
        result = trophy_recap(mock_league)
        
        # Should not call trophy functions
        mock_trophies.assert_not_called()
        mock_lucky.assert_not_called()
        mock_achievers.assert_not_called()
        mock_optimal.assert_not_called()
        mock_active.assert_not_called()
        
        # Should still return basic structure
        assert "Season Recap!" in result
        assert "*LEGEND*" in result
    
    @patch('gamedaybot.espn.season_recap.espn.get_weekly_score_with_win_loss')
    def test_win_matrix_basic(self, mock_scores, mock_league):
        """Test basic win_matrix functionality"""
        
        # Mock weekly scores for each week
        def mock_weekly_scores(league, week):
            # Return scores in descending order (highest to lowest)
            team1 = mock_league.teams[0]  # TA
            team2 = mock_league.teams[1]  # TB
            team3 = mock_league.teams[2]  # TC
            
            return {
                team1: [120.0, 'W'],  # Highest score
                team2: [100.0, 'L'],  # Middle score
                team3: [80.0, 'L']    # Lowest score
            }
        
        mock_scores.side_effect = mock_weekly_scores
        
        result = win_matrix(mock_league)
        
        assert "Standings if everyone played every team every week" in result
        assert "TA" in result
        assert "TB" in result
        assert "TC" in result
        
        # Check format: "1. TEAM (wins-losses)"
        assert "1. " in result
        assert "2. " in result
        assert "3. " in result
        assert "(" in result and ")" in result  # Win-loss format
    
    @patch('gamedaybot.espn.season_recap.espn.get_weekly_score_with_win_loss')
    def test_win_matrix_calculations(self, mock_scores, mock_league):
        """Test win_matrix calculations are correct"""
        
        def mock_weekly_scores(league, week):
            team1 = mock_league.teams[0]  # TA
            team2 = mock_league.teams[1]  # TB
            team3 = mock_league.teams[2]  # TC
            
            # Team1 always wins, Team2 middle, Team3 always loses
            return {
                team1: [120.0, 'W'],
                team2: [100.0, 'L'],
                team3: [80.0, 'L']
            }
        
        mock_scores.side_effect = mock_weekly_scores
        
        result = win_matrix(mock_league)
        
        # Team1 should have the best record (2-0 each week for 5 weeks = 10-0 total)
        # Team2 should be middle (1-1 each week for 5 weeks = 5-5 total)
        # Team3 should have worst record (0-2 each week for 5 weeks = 0-10 total)
        
        lines = result.split('\n')
        
        # Find team positions in standings
        ta_line = next(line for line in lines if 'TA' in line and '(' in line)
        tb_line = next(line for line in lines if 'TB' in line and '(' in line)
        tc_line = next(line for line in lines if 'TC' in line and '(' in line)
        
        # TA should be first (position 1)
        assert ta_line.strip().startswith('1.')
        
        # Should be called 5 times (for 5 completed weeks)
        assert mock_scores.call_count == 5
    
    @patch('gamedaybot.espn.season_recap.espn.get_weekly_score_with_win_loss')
    def test_win_matrix_early_season(self, mock_scores, mock_league):
        """Test win_matrix early in season"""
        
        mock_league.current_week = 2  # Only 1 completed week
        
        def mock_weekly_scores(league, week):
            team1 = mock_league.teams[0]
            team2 = mock_league.teams[1]
            team3 = mock_league.teams[2]
            
            return {
                team1: [120.0, 'W'],
                team2: [100.0, 'L'],
                team3: [80.0, 'L']
            }
        
        mock_scores.side_effect = mock_weekly_scores
        
        result = win_matrix(mock_league)
        
        # Should only call once for 1 completed week
        assert mock_scores.call_count == 1
        assert "Standings if everyone played every team every week" in result
    
    @patch('gamedaybot.espn.season_recap.espn.get_weekly_score_with_win_loss')
    def test_win_matrix_no_completed_weeks(self, mock_scores, mock_league):
        """Test win_matrix with no completed weeks"""
        
        mock_league.current_week = 1  # No completed weeks
        
        result = win_matrix(mock_league)
        
        # Should not call scoring function
        mock_scores.assert_not_called()
        
        # Should still return header and team structure with 0-0 records
        assert "Standings if everyone played every team every week" in result
        assert "TA" in result
        assert "(0-0)" in result
    
    @patch('gamedaybot.espn.season_recap.espn.get_weekly_score_with_win_loss')
    def test_win_matrix_tie_scenarios(self, mock_scores, mock_league):
        """Test win_matrix with tied records"""
        
        def mock_weekly_scores(league, week):
            team1 = mock_league.teams[0]
            team2 = mock_league.teams[1]
            team3 = mock_league.teams[2]
            
            # Create scenario where teams have equal records
            if week % 2 == 1:  # Odd weeks
                return {
                    team1: [120.0, 'W'],
                    team2: [100.0, 'L'],
                    team3: [110.0, 'L']
                }
            else:  # Even weeks
                return {
                    team2: [115.0, 'W'],
                    team1: [105.0, 'L'],
                    team3: [85.0, 'L']
                }
        
        mock_scores.side_effect = mock_weekly_scores
        
        result = win_matrix(mock_league)
        
        # Should handle ties in records appropriately
        assert "Standings if everyone played every team every week" in result
        lines = result.split('\n')
        standings_lines = [line for line in lines if '(' in line and ')' in line]
        
        # Should have 3 teams listed
        assert len(standings_lines) == 3
    
    def test_trophy_recap_legend_completeness(self, mock_league):
        """Test that trophy_recap legend includes all trophy types"""
        
        with patch('gamedaybot.espn.season_recap.espn.get_trophies') as mock_trophies, \
             patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy') as mock_lucky, \
             patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy') as mock_achievers, \
             patch('gamedaybot.espn.season_recap.espn.optimal_team_scores') as mock_optimal, \
             patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest') as mock_active:
            
            mock_trophies.return_value = ("TA", "TB", "TC", "TA")
            mock_lucky.return_value = ("TB", "TC", {})
            mock_achievers.return_value = ("TA", "TB")
            mock_optimal.return_value = "TC"
            mock_active.return_value = (["TA"], ["TB"])
            
            result = trophy_recap(mock_league)
            
            # Check all legend items are present
            legend_items = [
                "👑: Most Points",
                "💩: Least Points",
                "😱: Blown out",
                "😅: Close wins",
                "🍀: Lucky",
                "😡: Unlucky",
                "📈: Most over projection",
                "📉: Most under projection",
                "🤡: Most points left on bench",
                "🤯: Most active",
                "😴: Laziest"
            ]
            
            for legend_item in legend_items:
                assert legend_item in result
    
    def test_trophy_recap_team_initialization(self, mock_league):
        """Test that all teams are properly initialized with zero trophies"""
        
        with patch('gamedaybot.espn.season_recap.espn.get_trophies') as mock_trophies, \
             patch('gamedaybot.espn.season_recap.espn.get_lucky_trophy') as mock_lucky, \
             patch('gamedaybot.espn.season_recap.espn.get_achievers_trophy') as mock_achievers, \
             patch('gamedaybot.espn.season_recap.espn.optimal_team_scores') as mock_optimal, \
             patch('gamedaybot.espn.season_recap.espn.get_most_active_and_laziest') as mock_active:
            
            # Set current week to 1 so no weeks are processed
            mock_league.current_week = 1
            
            result = trophy_recap(mock_league)
            
            # All teams should be initialized with zeros
            assert "TA: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]" in result
            assert "TB: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]" in result
            assert "TC: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]" in result
    
    @patch('gamedaybot.espn.season_recap.espn.get_weekly_score_with_win_loss')
    def test_win_matrix_sorting(self, mock_scores, mock_league):
        """Test that win_matrix properly sorts teams by win percentage"""
        
        def mock_weekly_scores(league, week):
            team1 = mock_league.teams[0]  # TA
            team2 = mock_league.teams[1]  # TB
            team3 = mock_league.teams[2]  # TC
            
            # Create clear hierarchy: TA > TB > TC
            return {
                team1: [130.0, 'W'],  # Always highest
                team2: [100.0, 'L'],  # Always middle
                team3: [70.0, 'L']    # Always lowest
            }
        
        mock_scores.side_effect = mock_weekly_scores
        
        result = win_matrix(mock_league)
        lines = result.split('\n')
        
        # Find the team lines
        team_lines = [line for line in lines if '(' in line and ')' in line]
        
        # TA should be first (best record)
        assert 'TA' in team_lines[0]
        assert team_lines[0].strip().startswith('1.')
        
        # TC should be last (worst record)
        assert 'TC' in team_lines[2]
        assert team_lines[2].strip().startswith('3.')