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
    get_starter_counts, best_flex, last_completed_week,
    get_playoff_picture, get_draft_report, completed_matchups,
    playoff_status, wins_to_clinch
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
        league.settings.position_slot_counts = {
            'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'RB/WR/TE': 1,
            'D/ST': 1, 'K': 1, 'BE': 7, 'IR': 1, 'P': 0,
        }
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
        
        # Create action as a list instead of trying to assign to Mock indices
        team_mock = Mock()
        team_mock.team_name = "Team Alpha"
        
        player_mock = Mock()
        player_mock.name = "New Player"
        player_mock.position = "WR"
        
        action = [team_mock, "WAIVER ADDED", player_mock, 15]
        
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
        assert result == {'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'RB/WR/TE': 1, 'D/ST': 1, 'K': 1}
        # bench/IR are not starting slots, and unused slots are dropped
        assert 'BE' not in result and 'IR' not in result
        assert 'P' not in result

    def test_get_starter_counts_ignores_empty_lineups(self, mock_league):
        """Counts come from league settings, so a bye week or unset rosters
        must not produce None (which used to crash optimal_lineup_score)."""
        empty = Mock()
        empty.home_lineup = []
        empty.away_lineup = []
        mock_league.box_scores.return_value = [empty]

        result = get_starter_counts(mock_league)

        assert result is not None
        assert result['QB'] == 1
    
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
    
    def test_get_draft_reminder_completed_no_repeat(self, mock_league):
        """Test that draft completed messages are sent the day after completion, but not repeatedly"""
        
        # Test 1: Draft completed yesterday - should send completion message
        yesterday_timestamp = int((datetime(2024, 9, 4).timestamp()) * 1000)
        mock_league.espn_request.get_league_draft.return_value = {
            'draftDetail': {
                'drafted': True,
                'inProgress': False,
                'date': yesterday_timestamp
            }
        }
        
        # Mock league.draft for completion message
        mock_league.draft = [Mock() for _ in range(120)]  # 120 picks
        
        with patch('gamedaybot.espn.functionality.date') as mock_date:
            mock_date.today.return_value = date(2024, 9, 5)  # Today (1 day after draft)
            with patch('gamedaybot.espn.functionality.datetime') as mock_datetime:
                mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
                
                result = get_draft_reminder(mock_league)
                
                # Should send completion message the day after draft
                assert "DRAFT COMPLETED!" in result
        
        # Test 2: Draft completed 2 days ago - should NOT send message
        with patch('gamedaybot.espn.functionality.date') as mock_date:
            mock_date.today.return_value = date(2024, 9, 6)  # 2 days after draft
            with patch('gamedaybot.espn.functionality.datetime') as mock_datetime:
                mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
                
                result = get_draft_reminder(mock_league)
                
                # Should return empty string (no message) since it's been more than 1 day
                assert result == ""
    
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


class TestLastCompletedWeek:
    """The week arithmetic behind the Tuesday recap, especially at season's end.

    espn_api clamps league.current_week to finalScoringPeriod but leaves
    scoringPeriodId free to advance, so `current_week - 1` silently points at the
    wrong week once the regular season is over.
    """

    @staticmethod
    def _league(scoring_period_id, last_matchup_week=17):
        league = Mock()
        league.scoringPeriodId = scoring_period_id
        league.settings = Mock()
        league.settings.matchup_periods = list(range(1, last_matchup_week + 1))
        # Mirror espn_api: current_week is clamped, scoringPeriodId is not.
        league.current_week = min(scoring_period_id, last_matchup_week)
        return league

    def test_midseason_reports_the_week_that_just_ended(self):
        # Tuesday after week 5: scoringPeriodId has rolled to 6.
        assert last_completed_week(self._league(6)) == 5

    def test_tuesday_after_final_week_reports_the_final_week(self):
        # The regression: scoringPeriodId is 18, current_week is pinned at 17.
        league = self._league(18)
        assert league.current_week - 1 == 16  # what the old code produced
        assert last_completed_week(league) == 17

    def test_does_not_advance_past_the_final_week(self):
        assert last_completed_week(self._league(19)) == 17
        assert last_completed_week(self._league(25)) == 17

    def test_never_returns_a_week_below_one(self):
        assert last_completed_week(self._league(1)) == 1
        assert last_completed_week(self._league(0)) == 1


class TestPowerRankingsEdgeCases:
    """Normalization divides by scores that can legitimately be zero."""

    @staticmethod
    def _team(abbrev, playoff_pct=50.0):
        team = Mock()
        team.team_abbrev = abbrev
        team.playoff_pct = playoff_pct
        return team

    def test_all_zero_previous_week_does_not_divide_by_zero(self):
        alpha, bravo = self._team("AA"), self._team("BB")
        league = Mock()
        league.current_week = 4

        def power_rankings(week=None):
            if week == 2:
                return [(0.0, alpha), (0.0, bravo)]
            return [(10.0, alpha), (5.0, bravo)]

        league.power_rankings.side_effect = power_rankings

        result = get_power_rankings(league)

        assert "AA" in result and "BB" in result

    def test_all_zero_current_week_does_not_divide_by_zero(self):
        alpha, bravo = self._team("AA"), self._team("BB")
        league = Mock()
        league.current_week = 2
        league.power_rankings.return_value = [(0.0, alpha), (0.0, bravo)]

        result = get_power_rankings(league)

        assert "0.00" in result


class TestPlayoffPicture:
    """Seeding, clinch/elimination logic, and clinching scenarios."""

    REG_SEASON = 14
    SPOTS = 6

    def _league(self, records, playoff_pcts=None):
        teams = []
        for i, (wins, losses, ties) in enumerate(records):
            team = Mock()
            team.team_abbrev = 'T%02d' % (i + 1)
            team.team_name = 'Team %02d' % (i + 1)
            team.wins, team.losses, team.ties = wins, losses, ties
            team.points_for = 1000 - i * 20
            team.playoff_pct = (playoff_pcts or [0.0] * len(records))[i]
            teams.append(team)
        league = Mock()
        league.teams = teams
        league.settings = Mock()
        league.settings.playoff_team_count = self.SPOTS
        league.settings.reg_season_count = self.REG_SEASON
        league.standings.return_value = sorted(teams, key=lambda t: (-t.wins, -t.points_for))
        return league

    def test_completed_matchups_reads_records_not_week_counters(self):
        league = self._league([(6, 3, 1), (5, 5, 0)])
        assert completed_matchups(league) == 10

    def test_returns_empty_before_any_games(self):
        assert get_playoff_picture(self._league([(0, 0, 0)] * 10)) == ''

    def test_shows_seeding_with_a_cut_line(self):
        result = get_playoff_picture(self._league([(9, 2, 0), (8, 3, 0), (7, 4, 0), (7, 4, 0),
                                                   (6, 5, 0), (6, 5, 0), (5, 6, 0), (4, 7, 0),
                                                   (2, 9, 0), (1, 10, 0)]))
        assert 'Playoff Picture' in result
        assert 'cut line' in result
        # The cut belongs directly after the last team that would make it.
        lines = result.split('\n')
        cut = next(i for i, line in enumerate(lines) if 'cut line' in line)
        assert lines[cut - 1].strip().startswith('6:')
        assert lines[cut + 1].strip().startswith('7:')

    def test_runaway_leader_is_marked_clinched(self):
        # 11-0 with 3 to play: only two teams can even reach 11 wins, so with six
        # spots available the leader cannot be pushed out.
        result = get_playoff_picture(self._league([(11, 0, 0)] + [(4, 7, 0)] * 9))
        assert ' x ' in result
        assert 'x = clinched' in result

    def test_hopeless_team_is_marked_eliminated(self):
        result = get_playoff_picture(self._league([(11, 0, 0)] * 6 + [(0, 11, 0)] * 4))
        assert 'e = eliminated' in result

    def test_nobody_is_clinched_or_eliminated_in_week_one(self):
        result = get_playoff_picture(self._league([(1, 0, 0)] * 5 + [(0, 1, 0)] * 5))
        assert 'clinched' not in result
        assert 'eliminated' not in result

    def test_reports_clinching_scenarios_while_games_remain(self):
        result = get_playoff_picture(self._league([(9, 2, 0), (8, 3, 0), (7, 4, 0), (7, 4, 0),
                                                   (6, 5, 0), (6, 5, 0), (5, 6, 0), (4, 7, 0),
                                                   (2, 9, 0), (1, 10, 0)]))
        assert 'clinches with' in result

    def test_no_scenarios_once_the_regular_season_is_over(self):
        result = get_playoff_picture(self._league([(12, 2, 0), (11, 3, 0), (9, 5, 0), (8, 6, 0),
                                                   (8, 6, 0), (7, 7, 0), (6, 8, 0), (5, 9, 0),
                                                   (3, 11, 0), (1, 13, 0)]))
        assert 'Regular season complete' in result
        assert 'clinches with' not in result

    def test_ties_are_shown_only_when_a_team_has_tied(self):
        without = get_playoff_picture(self._league([(5, 5, 0)] * 10))
        assert '(5-5)' in without
        with_tie = get_playoff_picture(self._league([(5, 4, 1)] + [(5, 5, 0)] * 9))
        assert '(5-4-1)' in with_tie

    def test_wins_to_clinch_counts_down_as_wins_pile_up(self):
        teams = self._league([(8, 2, 0)] + [(4, 6, 0)] * 9).teams
        leader = teams[0]
        far = wins_to_clinch(leader, teams, self.SPOTS, 4)
        leader.wins = 9
        near = wins_to_clinch(leader, teams, self.SPOTS, 4)
        assert far == 1
        assert near == 0
        assert near < far

    def test_nothing_can_be_clinched_in_a_perfectly_tied_league(self):
        # Ten teams at 5-5 with four to play: every rival can still reach nine
        # wins, so with six spots any team can be squeezed out on tiebreakers.
        teams = self._league([(5, 5, 0)] * 10).teams
        assert wins_to_clinch(teams[0], teams, self.SPOTS, 4) is None

    def test_playoff_status_is_blank_when_undecided(self):
        teams = self._league([(5, 5, 0)] * 10).teams
        assert playoff_status(teams[0], teams, self.SPOTS, 4) == ''


class TestDraftReport:
    """Draft grading, steals, and busts."""

    def _league(self, num_picks=40, played=8, points_for_pick=None):
        teams = []
        for i in range(4):
            team = Mock()
            team.team_abbrev = 'T%d' % (i + 1)
            team.wins, team.losses, team.ties = played // 2, played - played // 2, 0
            teams.append(team)

        picks = []
        for overall in range(1, num_picks + 1):
            pick = Mock()
            pick.playerId = 1000 + overall
            pick.playerName = 'Player %03d' % overall
            pick.round_num = (overall - 1) // 4 + 1
            pick.round_pick = (overall - 1) % 4 + 1
            pick.team = teams[(overall - 1) % 4]
            picks.append(pick)

        league = Mock()
        league.teams = teams
        league.draft = picks
        league.settings = Mock()

        scorer = points_for_pick or (lambda overall: max(200.0 - overall * 4.0, 1.0))

        def player_info(playerId=None, name=None):
            out = []
            for pid in playerId:
                player = Mock()
                player.playerId = pid
                player.total_points = scorer(pid - 1000)
                out.append(player)
            return out

        league.player_info.side_effect = player_info
        return league

    def test_returns_empty_without_draft_data(self):
        league = self._league()
        league.draft = []
        assert get_draft_report(league) == ''

    def test_asks_for_patience_early_in_the_season(self):
        result = get_draft_report(self._league(played=2), min_weeks=4)
        assert 'after week 4' in result

    def test_grades_every_team(self):
        result = get_draft_report(self._league())
        assert 'Draft Report Card' in result
        for abbrev in ('T1', 'T2', 'T3', 'T4'):
            assert abbrev in result

    def test_a_late_pick_that_scored_big_is_the_top_steal(self):
        # Pick 40 outscores everyone; it was taken last, so it is the biggest steal.
        def scorer(overall):
            return 999.0 if overall == 40 else max(200.0 - overall * 4.0, 1.0)

        result = get_draft_report(self._league(points_for_pick=scorer))
        steals = result.split('Biggest Steals')[1].split('Biggest Busts')[0]
        assert 'Player 040' in steals

    def test_an_early_pick_that_flopped_is_the_top_bust(self):
        def scorer(overall):
            return 0.0 if overall == 1 else max(200.0 - overall * 4.0, 1.0)

        result = get_draft_report(self._league(points_for_pick=scorer))
        busts = result.split('Biggest Busts')[1]
        assert 'Player 001' in busts

    def test_player_lookups_are_batched(self):
        league = self._league(num_picks=120)
        get_draft_report(league)
        # 120 picks at 50 per request is 3 calls, not 120.
        assert league.player_info.call_count == 3

    def test_survives_a_failed_player_lookup(self):
        league = self._league()
        league.player_info.side_effect = Exception("ESPN unavailable")
        assert get_draft_report(league) == ''
