import pytest
import sys
import os
sys.path.insert(1, os.path.abspath('.'))

import unittest.mock as mock
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from discord.ext import commands
from discord import app_commands

from gamedaybot.chat.discord_bot import FantasyFootballCog
from espn_api.football import League, Team, Player


class TestFantasyFootballCog:
    """Test FantasyFootballCog Discord bot commands"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Mock bot
        self.mock_bot = MagicMock(spec=commands.Bot)
        self.mock_bot.tree = MagicMock()
        self.mock_bot.tree.sync = AsyncMock()
        
        # Mock league with comprehensive data
        self.mock_league = MagicMock(spec=League)
        self.mock_league.league_id = 123456
        self.mock_league.year = 2023
        self.mock_league.current_week = 5
        
        # Mock teams
        self.mock_team1 = MagicMock(spec=Team)
        self.mock_team1.team_name = "Team Alpha"
        self.mock_team1.owner = "Owner1"
        self.mock_team1.wins = 3
        self.mock_team1.losses = 1
        
        self.mock_team2 = MagicMock(spec=Team)
        self.mock_team2.team_name = "Team Beta"
        self.mock_team2.owner = "Owner2"
        self.mock_team2.wins = 2
        self.mock_team2.losses = 2
        
        self.mock_league.teams = [self.mock_team1, self.mock_team2]
        
        # Guild ID
        self.guild_id = 987654321
        
        # Create cog instance
        self.cog = FantasyFootballCog(self.mock_bot, self.mock_league, self.guild_id)
        
        # Mock interaction
        self.mock_interaction = AsyncMock()
        self.mock_interaction.response.send_message = AsyncMock()
        self.mock_interaction.response.defer = AsyncMock()
        self.mock_interaction.followup.send_message = AsyncMock()

    def test_init(self):
        """Test FantasyFootballCog initialization"""
        assert self.cog.bot == self.mock_bot
        assert self.cog.league == self.mock_league
        assert isinstance(self.cog.guild, discord.Object)
        assert self.cog.guild.id == self.guild_id

    @patch('gamedaybot.espn.functionality.get_scoreboard_short')
    @pytest.mark.asyncio
    async def test_current_scores(self, mock_get_scoreboard):
        """Test current_scores command"""
        mock_get_scoreboard.return_value = "Team Alpha: 125.5 vs Team Beta: 110.2"
        
        await self.cog.current_scores.callback(self.cog, self.mock_interaction)
        
        mock_get_scoreboard.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()
        
        # Check that message is wrapped in codeblock
        call_args = self.mock_interaction.response.send_message.call_args[0][0]
        assert call_args.startswith("```")
        assert call_args.endswith("```")
        assert "Team Alpha: 125.5 vs Team Beta: 110.2" in call_args

    @patch('gamedaybot.espn.functionality.get_scoreboard_short')
    @pytest.mark.asyncio
    async def test_scoreboard(self, mock_get_scoreboard):
        """Test scoreboard command with specific week"""
        week = 3
        mock_get_scoreboard.return_value = "Week 3 scoreboard data"
        
        await self.cog.scoreboard.callback(self.cog, self.mock_interaction, week)
        
        mock_get_scoreboard.assert_called_once_with(self.mock_league, week)
        self.mock_interaction.response.send_message.assert_called_once()
        
        call_args = self.mock_interaction.response.send_message.call_args[0][0]
        assert f"Week {week}" in call_args
        assert "Week 3 scoreboard data" in call_args

    @patch('gamedaybot.espn.functionality.get_projected_scoreboard')
    @pytest.mark.asyncio
    async def test_projected_scores(self, mock_get_projected):
        """Test projected_scores command"""
        mock_get_projected.return_value = "Projected: Team Alpha: 130.0 vs Team Beta: 115.5"
        
        await self.cog.projected_scores.callback(self.cog, self.mock_interaction)
        
        mock_get_projected.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()
        
        call_args = self.mock_interaction.response.send_message.call_args[0][0]
        assert "Projected: Team Alpha: 130.0 vs Team Beta: 115.5" in call_args

    @patch('gamedaybot.espn.functionality.get_standings')
    @pytest.mark.asyncio
    async def test_standings(self, mock_get_standings):
        """Test standings command"""
        mock_get_standings.return_value = "1. Team Alpha (3-1)\n2. Team Beta (2-2)"
        
        await self.cog.standings.callback(self.cog, self.mock_interaction)
        
        mock_get_standings.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_monitor')
    @pytest.mark.asyncio
    async def test_players_to_monitor(self, mock_get_monitor):
        """Test players_to_monitor command"""
        mock_get_monitor.return_value = "Players to monitor: Player A (Questionable), Player B (Doubtful)"
        
        await self.cog.players_to_monitor.callback(self.cog, self.mock_interaction)
        
        mock_get_monitor.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_matchups')
    @pytest.mark.asyncio
    async def test_matchups(self, mock_get_matchups):
        """Test matchups command"""
        mock_get_matchups.return_value = "Week 5 Matchups:\nTeam Alpha vs Team Beta"
        
        await self.cog.matchups.callback(self.cog, self.mock_interaction)
        
        mock_get_matchups.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_close_scores')
    @pytest.mark.asyncio
    async def test_close_scores(self, mock_get_close):
        """Test close_scores command"""
        mock_get_close.return_value = "Close matchups: Team Alpha (125.5) vs Team Beta (123.2)"
        
        await self.cog.close_scores.callback(self.cog, self.mock_interaction)
        
        mock_get_close.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_power_rankings')
    @pytest.mark.asyncio
    async def test_power_rankings(self, mock_get_power):
        """Test power_rankings command"""
        mock_get_power.return_value = "Power Rankings:\n1. Team Alpha\n2. Team Beta"
        
        await self.cog.power_rankings.callback(self.cog, self.mock_interaction)
        
        mock_get_power.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_player_status')
    @pytest.mark.asyncio
    async def test_player_status(self, mock_get_status):
        """Test player_status command"""
        player_name = "Christian McCaffrey"
        status = "Active"
        mock_get_status.return_value = status
        
        await self.cog.player_status.callback(self.cog, self.mock_interaction, player_name)
        
        mock_get_status.assert_called_once_with(self.mock_league, player_name)
        self.mock_interaction.response.send_message.assert_called_once()
        
        call_args = self.mock_interaction.response.send_message.call_args[0][0]
        assert player_name in call_args
        assert status in call_args

    @patch('gamedaybot.espn.functionality.get_lineup')
    @pytest.mark.asyncio
    async def test_lineup_without_week(self, mock_get_lineup):
        """Test lineup command without specifying week"""
        team_name = "Team Alpha"
        mock_get_lineup.return_value = "Team Alpha Lineup:\nQB: Player1\nRB: Player2"
        
        await self.cog.lineup.callback(self.cog, self.mock_interaction, team_name)
        
        mock_get_lineup.assert_called_once_with(self.mock_league, team_name, None)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_lineup')
    @pytest.mark.asyncio
    async def test_lineup_with_week(self, mock_get_lineup):
        """Test lineup command with specific week"""
        team_name = "Team Alpha"
        week = 4
        mock_get_lineup.return_value = "Team Alpha Week 4 Lineup:\nQB: Player1\nRB: Player2"
        
        await self.cog.lineup.callback(self.cog, self.mock_interaction, team_name, week)
        
        mock_get_lineup.assert_called_once_with(self.mock_league, team_name, week)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.season_recap.trophy_recap')
    @pytest.mark.asyncio
    async def test_recap(self, mock_trophy_recap):
        """Test recap command"""
        mock_trophy_recap.return_value = "Season Recap:\nChampion: Team Alpha\nMost Points: Team Beta"
        
        await self.cog.recap.callback(self.cog, self.mock_interaction)
        
        mock_trophy_recap.assert_called_once_with(self.mock_league)
        # Note: recap uses defer() then followup.send_message()
        self.mock_interaction.response.defer.assert_called_once()
        self.mock_interaction.followup.send_message.assert_called_once()

    @patch('gamedaybot.espn.season_recap.win_matrix')
    @pytest.mark.asyncio
    async def test_win_matrix(self, mock_win_matrix):
        """Test win_matrix command"""
        mock_win_matrix.return_value = "Win Matrix:\n    A B\nA   - W\nB   L -"
        
        await self.cog.win_matrix.callback(self.cog, self.mock_interaction)
        
        mock_win_matrix.assert_called_once_with(self.mock_league)
        # Note: win_matrix uses defer() then followup.send_message()
        self.mock_interaction.response.defer.assert_called_once()
        self.mock_interaction.followup.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_team_names')
    @pytest.mark.asyncio
    async def test_team_names_autocomplete(self, mock_get_team_names):
        """Test team_names_autocomplete for lineup command"""
        mock_get_team_names.return_value = ["Team Alpha", "Team Beta", "Team Gamma"]
        current_input = "alph"
        
        result = await self.cog.team_names_autocomplete(self.mock_interaction, current_input)
        
        mock_get_team_names.assert_called_once_with(self.mock_league)
        assert len(result) == 1
        assert result[0].name == "Team Alpha"
        assert result[0].value == "Team Alpha"

    @patch('gamedaybot.espn.functionality.get_team_names')
    @pytest.mark.asyncio
    async def test_team_names_autocomplete_case_insensitive(self, mock_get_team_names):
        """Test team_names_autocomplete is case insensitive"""
        mock_get_team_names.return_value = ["Team Alpha", "Team Beta", "Alpha Wolves"]
        current_input = "ALPHA"
        
        result = await self.cog.team_names_autocomplete(self.mock_interaction, current_input)
        
        assert len(result) == 2
        team_names = [choice.name for choice in result]
        assert "Team Alpha" in team_names
        assert "Alpha Wolves" in team_names

    @patch('gamedaybot.espn.functionality.get_team_names')
    @pytest.mark.asyncio
    async def test_team_names_autocomplete_no_matches(self, mock_get_team_names):
        """Test team_names_autocomplete with no matches"""
        mock_get_team_names.return_value = ["Team Alpha", "Team Beta"]
        current_input = "xyz"
        
        result = await self.cog.team_names_autocomplete(self.mock_interaction, current_input)
        
        assert len(result) == 0

    @patch('gamedaybot.espn.functionality.get_cmc_still_injured')
    @pytest.mark.asyncio
    async def test_cmc_command(self, mock_get_cmc):
        """Test cmc command"""
        mock_get_cmc.return_value = "CMC Status: Active and healthy!"
        
        await self.cog.cmc.callback(self.cog, self.mock_interaction)
        
        mock_get_cmc.assert_called_once_with(self.mock_league)
        self.mock_interaction.response.send_message.assert_called_once()

    def test_codeblock_static_method(self):
        """Test codeblock static method"""
        test_string = "This is a test string"
        result = FantasyFootballCog.codeblock(test_string)
        
        assert result == "```This is a test string```"

    def test_codeblock_with_empty_string(self):
        """Test codeblock with empty string"""
        result = FantasyFootballCog.codeblock("")
        assert result == "``````"

    def test_codeblock_with_multiline_string(self):
        """Test codeblock with multiline string"""
        test_string = "Line 1\nLine 2\nLine 3"
        result = FantasyFootballCog.codeblock(test_string)
        
        assert result == "```Line 1\nLine 2\nLine 3```"

    @pytest.mark.asyncio
    async def test_on_ready_event(self):
        """Test on_ready event listener"""
        # This tests the guild sync functionality
        await self.cog.on_ready()
        
        # Verify that tree operations were called
        self.mock_bot.tree.copy_global_to.assert_called_once_with(guild=self.cog.guild)
        self.mock_bot.tree.sync.assert_called_once_with(guild=self.cog.guild)

    @patch('gamedaybot.espn.functionality.get_scoreboard_short')
    @pytest.mark.asyncio
    async def test_command_error_handling(self, mock_get_scoreboard):
        """Test command behavior when ESPN function raises exception"""
        # Mock the ESPN function to raise an exception
        mock_get_scoreboard.side_effect = Exception("ESPN API Error")
        
        # The exception should propagate up to Discord's error handler
        with pytest.raises(Exception, match="ESPN API Error"):
            await self.cog.current_scores.callback(self.cog, self.mock_interaction)

    @pytest.mark.asyncio
    async def test_interaction_response_called_once(self):
        """Test that interaction.response.send_message is only called once per command"""
        with patch('gamedaybot.espn.functionality.get_standings') as mock_standings:
            mock_standings.return_value = "Test standings"
            
            await self.cog.standings.callback(self.cog, self.mock_interaction)
            
            # Ensure response is sent exactly once
            assert self.mock_interaction.response.send_message.call_count == 1

    def test_guild_object_creation(self):
        """Test that guild object is created correctly"""
        guild_id = 123456789
        cog = FantasyFootballCog(self.mock_bot, self.mock_league, guild_id)
        
        assert isinstance(cog.guild, discord.Object)
        assert cog.guild.id == guild_id

    @pytest.mark.asyncio
    async def test_deferred_response_commands(self):
        """Test commands that use deferred responses"""
        with patch('gamedaybot.espn.season_recap.trophy_recap') as mock_recap:
            mock_recap.return_value = "Test recap"
            
            await self.cog.recap.callback(self.cog, self.mock_interaction)
            
            # Verify defer was called before followup
            self.mock_interaction.response.defer.assert_called_once()
            self.mock_interaction.followup.send_message.assert_called_once()
            # Ensure regular send_message was not called for deferred commands
            assert self.mock_interaction.response.send_message.call_count == 0

    @patch('gamedaybot.espn.functionality.get_team_names')
    @pytest.mark.asyncio
    async def test_autocomplete_with_empty_current(self, mock_get_team_names):
        """Test autocomplete with empty current string"""
        mock_get_team_names.return_value = ["Team Alpha", "Team Beta"]
        
        result = await self.cog.team_names_autocomplete(self.mock_interaction, "")
        
        # Should return all teams when current is empty
        assert len(result) == 2

    def test_repr_methods(self):
        """Test that the cog can be represented as string"""
        # This ensures the object can be debugged/logged properly
        cog_str = str(self.cog)
        assert "FantasyFootballCog" in cog_str or "object at" in cog_str

    @patch('gamedaybot.espn.functionality.get_lineup')
    @pytest.mark.asyncio
    async def test_lineup_with_special_characters(self, mock_get_lineup):
        """Test lineup command with team name containing special characters"""
        team_name = "Team O'Malley & Sons"
        mock_get_lineup.return_value = "Lineup for Team O'Malley & Sons"
        
        await self.cog.lineup.callback(self.cog, self.mock_interaction, team_name)
        
        mock_get_lineup.assert_called_once_with(self.mock_league, team_name, None)
        self.mock_interaction.response.send_message.assert_called_once()

    @patch('gamedaybot.espn.functionality.get_player_status')
    @pytest.mark.asyncio
    async def test_player_status_with_special_characters(self, mock_get_status):
        """Test player_status command with special characters in name"""
        player_name = "D'Andre Swift"
        status = "Active"
        mock_get_status.return_value = status
        
        await self.cog.player_status.callback(self.cog, self.mock_interaction, player_name)
        
        mock_get_status.assert_called_once_with(self.mock_league, player_name)
        call_args = self.mock_interaction.response.send_message.call_args[0][0]
        assert player_name in call_args