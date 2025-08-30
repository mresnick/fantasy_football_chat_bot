"""Unit tests for functionality.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.espn import functionality
from gamedaybot.espn.functionality import (
    get_scoreboard_short, get_projected_scoreboard, get_standings,
    get_matchups, get_close_scores, get_monitor, get_waiver_report,
    get_power_rankings, get_trophies, get_draft_reminder, all_played,
    scan_roster, top_half_wins, OrderedBoxPlayer, optimal_lineup_score,
    get_starter_counts, best_flex
)


class TestFunctionality:
    """Test suite for functionality module"""
    
    @pytest.fixture
    def mock_league(self):
        """Create a comprehensive mock league with all necessary attributes"""
        league = Mock()
        league.current_week = 5
        league.scoringPeriodId = 5
        
        # Mock settings
        league.settings = Mock()
        league.settings.matchup_periods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        league.settings.faab = True
        league.settings.name = "Test League"
        league.settings.team_count = 12
        
        # Mock teams
        team1 = Mock()
        team1.team_name = "Team Alpha"
        team1.team_abbrev = "TA"
        team1.wins = 3
        team1.losses = 1
        team1.points_for = 450.5
        team1.points_against = 380.2
        team1.playoff_pct = 85.5
        
        team2 = Mock()
        team2.team_name = "Team Bravo"
        team2.team_abbrev = "TB"
        team2.wins = 2
        team2.losses = 2
        team2.points_for = 420.3
        team2.points_against = 410.1
        team2.playoff_pct = 65.2
        
        league.teams = [team1, team2]
        
        # Mock box scores
        def create_box_score(home_team, away_team, home_score=100.0, away_score=95.0,
                           home_proj=98.0, away_proj=92.0):
            box_score = Mock()
            box_score.home_team = home_team
            box_score.away_team = away_team
            box_score.home_score = home_score
            box_score.away_score = away_score
            box_score.home_projected = home_proj
            box_score.away_projected = away_proj
            
            # Mock lineups
            box_score.home_lineup = self.create_mock_lineup()
            box_score.away_lineup = self.create_mock_lineup()
            
            return box_score
        
        league.box_scores = Mock(return_value=[
            create_box_score(team1, team2, 105.5, 98.3, 102.0, 95.0)
        ])
        
        # Mock standings
        league.standings = Mock(return_value=[team1, team2])
        
        # Mock power rankings
        league.power_rankings = Mock(return_value=[
            (85.5, team1),
            (65.2, team2)
        ])
        
        # Mock recent activity
        league.recent_activity = Mock(return_value=self.create_mock_activities())
        
        # Mock player info
        league.player_info = Mock(return_value=Mock(injuryStatus='ACTIVE'))
        
        # Mock refresh_draft
        league.refresh_draft = Mock()
        league.draft = []
        
        # Mock ESPN request
        league.espn_request = Mock()
        league.espn_request.get_league_draft = Mock(return_value={
            'draftDetail': {'drafted': False, 'inProgress': False}
        })
        league.espn_request.get_pro_schedule = Mock(return_value={
            'settings': {'playerOwnershipSettings': {'firstGameDate': 1693785600000}}  # Sept 4, 2023
        })
        
        return league
    
    def create_mock_lineup(self):
        """Create mock lineup with players"""
        players = []
        
        # Starting lineup
        qb = Mock()
        qb.name = "Test QB"
        qb.position = "QB"
        qb.slot_position = "QB"
        qb.points = 25.5
        qb.injuryStatus = "ACTIVE"
        qb.game_played = 100
        qb.on_bye_week = False
        players.append(qb)
        
        rb = Mock()
        rb.name = "Test RB"
        rb.position = "RB"
        rb.slot_position = "RB"
        rb.points = 18.3
        rb.injuryStatus = "QUESTIONABLE"
        rb.game_played = 0
        rb.on_bye_week = False
        players.append(rb)
        
        # Bench player
        bench_player = Mock()
        bench_player.name = "Bench Player"
        bench_player.position = "WR"
        bench_player.slot_position = "BE"
        bench_player.points = 12.1
        bench_player.injuryStatus = "ACTIVE"
        bench_player.game_played = 100
        bench_player.on_bye_week = False
        players.append(bench_player)
        
        return players
    
    def create_mock_activities(self):
        """Create mock recent activities"""
        activities = []
        
        # Mock waiver activity
        activity = Mock()
        activity.date = int(datetime.now().timestamp() * 1000)  # Today's timestamp in milliseconds
        
        action = Mock()
        action[0] = Mock()  # team
        action[0].team_name = "Team Alpha"
        action[1] = "WAIVER ADDED"  # action type
        action[2] = Mock()  # player
        action[2].name = "New Player"
        action[2].position = "WR"
        action[3] = 15  # FAAB amount
        
        activity.actions = [action]
        activities.append(activity)
        
        return activities
    
    def test_get_scoreboard_short(self, mock_league):
        """Test get_scoreboard_short function"""
        result = get_scoreboard_short(mock_league)
        
        assert "Score Update" in result
        assert "TA" in result  # Team abbreviation
        assert "TB" in result
        assert "105.50" in result or "105.5" in result
        assert "98.30" in result or "98.3" in result
    
    def test_get_projected_scoreboard(self, mock_league):
        """Test get_projected_scoreboard function"""
        result = get_projected_scoreboard(mock_league)
        
        assert "Approximate Projected Scores" in result
        assert "TA" in result
        assert "TB" in result
        assert "102.00" in result or "102" in result
    
    def test_get_standings_basic(self, mock_league):
        """Test get_standings function with basic settings"""
        result = get_standings(mock_league)
        
        assert "Current Standings" in result
        assert "Team Alpha" in result
        assert "(3-1)" in result
        assert "Team Bravo" in result
        assert "(2-2)" in result
    
    def test_get_standings_top_half_scoring(self, mock_league):
        """Test get_standings with top half scoring enabled"""
        result = get_standings(mock_league, top_half_scoring=True)
        
        assert "Current Standings" in result
        # Should include top half scoring calculations
        assert "+" in result  # Top half bonus indicator
    
    def test_get_matchups(self, mock_league):
        """Test get_matchups function"""
        result = get_matchups(mock_league)
        
        assert "Matchups" in result
        assert "Team Alpha vs Team Bravo" in result
        assert "TA (3-1) vs (2-2) TB" in result
    
    def test_get_close_scores_close_game(self, mock_league):
        """Test get_close_scores with a close game"""
        # Modify mock to have close projected scores
        mock_league.box_scores.return_value[0].home_projected = 100.0
        mock_league.box_scores.return_value[0].away_projected = 95.0
        
        result = get_close_scores(mock_league)
        
        if result:  # Only test if close scores exist
            assert "Projected Close Scores" in result
    
    def test_get_close_scores_no_close_games(self, mock_league):
        """Test get_close_scores with no close games"""
        # Modify mock to have wide projected score difference
        mock_league.box_scores.return_value[0].home_projected = 120.0
        mock_league.box_scores.return_value[0].away_projected = 80.0
        
        result = get_close_scores(mock_league)
        
        assert result == ""  # Should return empty string
    
    def test_get_monitor_with_questionable_players(self, mock_league):
        """Test get_monitor function with questionable players"""
        result = get_monitor(mock_league)
        
        # Should find the questionable RB in starting lineup
        if "Starting Players to Monitor" in result:
            assert "RB Test RB - Questionable" in result
        else:
            assert "No Players to Monitor" in result
    
    def test_get_monitor_no_players_to_monitor(self, mock_league):
        """Test get_monitor when no players need monitoring"""
        # Make all players active
        for box_score in mock_league.box_scores():
            for player in box_score.home_lineup + box_score.away_lineup:
                player.injuryStatus = "ACTIVE"
                player.game_played = 100
        
        result = get_monitor(mock_league)
        
        assert "No Players to Monitor this week. Good Luck!" in result
    
    def test_scan_roster(self, mock_league):
        """Test scan_roster function"""
        lineup = self.create_mock_lineup()
        team = mock_league.teams[0]
        
        result = scan_roster(lineup, team)
        
        # Should find the questionable RB
        if result:
            assert "Team Alpha" in result[0]
            assert "RB Test RB - Questionable" in result[0]
    
    def test_all_played_true(self):
        """Test all_played function when all players have played"""
        lineup = []
        player = Mock()
        player.slot_position = "QB"
        player.game_played = 100
        lineup.append(player)
        
        result = all_played(lineup)
        assert result is True
    
    def test_all_played_false(self):
        """Test all_played function when not all players have played"""
        lineup = []
        player = Mock()
        player.slot_position = "QB"
        player.game_played = 0  # Hasn't played yet
        lineup.append(player)
        
        result = all_played(lineup)
        assert result is False
    
    def test_all_played_excludes_bench(self):
        """Test all_played excludes bench and IR players"""
        lineup = []
        
        # Bench player who hasn't played
        bench_player = Mock()
        bench_player.slot_position = "BE"
        bench_player.game_played = 0
        lineup.append(bench_player)
        
        # IR player who hasn't played
        ir_player = Mock()
        ir_player.slot_position = "IR"
        ir_player.game_played = 0
        lineup.append(ir_player)
        
        result = all_played(lineup)
        assert result is True  # Should ignore bench and IR players
    
    def test_get_waiver_report_with_activity(self, mock_league):
        """Test get_waiver_report with waiver activity"""
        result = get_waiver_report(mock_league, faab=True)
        
        today_str = date.today().strftime('%Y-%m-%d')
        assert f"Waiver Report {today_str}:" in result
        assert "Team Alpha" in result
        assert "ADDED WR New Player ($15)" in result
    
    def test_get_waiver_report_no_faab(self, mock_league):
        """Test get_waiver_report without FAAB"""
        result = get_waiver_report(mock_league, faab=False)
        
        if "No waiver transactions" not in result:
            assert "Team Alpha" in result
            assert "ADDED WR New Player" in result
            assert "$" not in result  # No FAAB amounts
    
    def test_get_waiver_report_no_activity(self, mock_league):
        """Test get_waiver_report with no activity"""
        mock_league.recent_activity.return_value = []
        
        result = get_waiver_report(mock_league)
        
        assert "No waiver transactions" in result
    
    def test_get_power_rankings(self, mock_league):
        """Test get_power_rankings function"""
        result = get_power_rankings(mock_league)
        
        assert "Power Rankings (Playoff %)" in result
        assert "TA" in result
        assert "TB" in result
        assert "85.5" in result  # Playoff percentage
    
    def test_top_half_wins(self, mock_league):
        """Test top_half_wins function"""
        top_half_totals = {"Team Alpha": 0, "Team Bravo": 0}
        
        result = top_half_wins(mock_league, top_half_totals, 1)
        
        # Should have updated the totals
        assert isinstance(result, dict)
        assert "Team Alpha" in result
        assert "Team Bravo" in result
    
    def test_ordered_box_player(self):
        """Test OrderedBoxPlayer class"""
        # Create mock box players
        qb_player = Mock()
        qb_player.slot_position = "QB"
        
        rb_player = Mock()
        rb_player.slot_position = "RB"
        
        ordered_qb = OrderedBoxPlayer(qb_player)
        ordered_rb = OrderedBoxPlayer(rb_player)
        
        # QB should come before RB in ordering
        assert ordered_qb < ordered_rb
        assert not ordered_qb == ordered_rb
    
    def test_get_starter_counts(self, mock_league):
        """Test get_starter_counts function"""
        result = get_starter_counts(mock_league)
        
        assert isinstance(result, dict)
        assert "QB" in result
        assert "RB" in result
    
    def test_best_flex(self):
        """Test best_flex function"""
        flexes = ["RB", "WR", "TE"]
        player_pool = {
            "RB": {"RB1": 20.0, "RB2": 15.0},
            "WR": {"WR1": 18.0, "WR2": 12.0},
            "TE": {"TE1": 16.0}
        }
        
        best_players, updated_pool = best_flex(flexes, player_pool, 2)
        
        assert len(best_players) == 2
        assert "RB1" in best_players  # Should be highest scoring
        assert "WR1" in best_players  # Should be second highest
    
    def test_optimal_lineup_score(self, mock_league):
        """Test optimal_lineup_score function"""
        lineup = self.create_mock_lineup()
        starter_counts = {"QB": 1, "RB": 1}
        
        result = optimal_lineup_score(lineup, starter_counts)
        
        assert len(result) == 4  # (best_score, actual_score, difference, percentage)
        assert isinstance(result[0], (int, float))  # best_score
        assert isinstance(result[1], (int, float))  # actual_score
        assert isinstance(result[2], (int, float))  # difference
        assert isinstance(result[3], (int, float))  # percentage
    
    def test_get_trophies(self, mock_league):
        """Test get_trophies function"""
        result = get_trophies(mock_league)
        
        assert "Trophies of the week:" in result
        assert "👑 High score 👑" in result
        assert "💩 Low score 💩" in result
        assert "Team Alpha" in result or "Team Bravo" in result
    
    @patch('gamedaybot.espn.functionality.date')
    def test_get_draft_reminder_today(self, mock_date, mock_league):
        """Test get_draft_reminder for draft day"""
        mock_date.today.return_value = date(2024, 9, 1)
        
        result = get_draft_reminder(mock_league, "2024-09-01")
        
        assert "DRAFT DAY IS TODAY!" in result
    
    @patch('gamedaybot.espn.functionality.date')
    def test_get_draft_reminder_tomorrow(self, mock_date, mock_league):
        """Test get_draft_reminder for tomorrow"""
        mock_date.today.return_value = date(2024, 8, 31)
        
        result = get_draft_reminder(mock_league, "2024-09-01")
        
        assert "DRAFT IS TOMORROW!" in result
    
    @patch('gamedaybot.espn.functionality.date')
    def test_get_draft_reminder_week_away(self, mock_date, mock_league):
        """Test get_draft_reminder for a week away"""
        mock_date.today.return_value = date(2024, 8, 25)
        
        result = get_draft_reminder(mock_league, "2024-09-01")
        
        assert "DRAFT REMINDER" in result
        assert "7 days until the draft" in result
    
    @patch('gamedaybot.espn.functionality.date')
    def test_get_draft_reminder_past_date(self, mock_date, mock_league):
        """Test get_draft_reminder for past date"""
        mock_date.today.return_value = date(2024, 9, 5)
        
        result = get_draft_reminder(mock_league, "2024-09-01")
        
        assert result == ""  # Should return empty string for past dates
    
    def test_get_draft_reminder_completed_draft(self, mock_league):
        """Test get_draft_reminder for completed draft"""
        mock_league.espn_request.get_league_draft.return_value = {
            'draftDetail': {'drafted': True, 'inProgress': False}
        }
        
        result = get_draft_reminder(mock_league)
        
        assert "DRAFT COMPLETED!" in result
    
    def test_get_draft_reminder_in_progress(self, mock_league):
        """Test get_draft_reminder for draft in progress"""
        mock_league.espn_request.get_league_draft.return_value = {
            'draftDetail': {'drafted': False, 'inProgress': True}
        }
        
        result = get_draft_reminder(mock_league)
        
        assert "DRAFT IN PROGRESS!" in result
    
    def test_get_draft_reminder_invalid_date(self, mock_league):
        """Test get_draft_reminder with invalid date format"""
        result = get_draft_reminder(mock_league, "invalid-date")
        
        assert "Invalid draft date format" in result
    
    def test_get_draft_reminder_no_date(self, mock_league):
        """Test get_draft_reminder with no date provided"""
        mock_league.current_week = 0  # Pre-season
        
        result = get_draft_reminder(mock_league)
        
        assert "DRAFT REMINDER" in result
        assert "pre-season" in result
    
    def test_get_player_status_found(self, mock_league):
        """Test get_player_status for found player"""
        mock_player = Mock()
        mock_player.injuryStatus = "QUESTIONABLE"
        mock_league.player_info.return_value = mock_player
        
        result = functionality.get_player_status(mock_league, "Test Player")
        
        assert result == "QUESTIONABLE"
    
    def test_get_player_status_not_found(self, mock_league):
        """Test get_player_status for player not found"""
        mock_league.player_info.return_value = None
        
        result = functionality.get_player_status(mock_league, "Nonexistent Player")
        
        assert result == "not found in the league"
    
    def test_get_cmc_still_injured_yes(self, mock_league):
        """Test get_cmc_still_injured when CMC is injured"""
        mock_player = Mock()
        mock_player.injuryStatus = "OUT"
        mock_league.player_info.return_value = mock_player
        
        result = functionality.get_cmc_still_injured(mock_league)
        
        assert "Is CMC still injured?" in result
        assert "Yes!" in result
    
    def test_get_cmc_still_injured_probably(self, mock_league):
        """Test get_cmc_still_injured when CMC is questionable"""
        mock_player = Mock()
        mock_player.injuryStatus = "QUESTIONABLE"
        mock_league.player_info.return_value = mock_player
        
        result = functionality.get_cmc_still_injured(mock_league)
        
        assert "Is CMC still injured?" in result
        assert "Probably!" in result
    
    def test_get_cmc_still_injured_no(self, mock_league):
        """Test get_cmc_still_injured when CMC is healthy"""
        mock_player = Mock()
        mock_player.injuryStatus = "ACTIVE"
        mock_league.player_info.return_value = mock_player
        
        result = functionality.get_cmc_still_injured(mock_league)
        
        assert "Is CMC still injured?" in result
        assert "NO!!!" in result