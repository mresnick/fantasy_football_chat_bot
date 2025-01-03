import discord
from discord.ext import commands
from discord import app_commands
import gamedaybot.espn.functionality as espn
import gamedaybot.espn.season_recap as recap
from espn_api.football import League
import logging


class FantasyFootballCog(commands.Cog):
    def __init__(self, bot, league, guild_id):
        self.bot = bot
        self.league = league
        self.guild = discord.Object(id=guild_id)

    @app_commands.command(description="Get current scores for the week.")
    async def current_scores(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_scoreboard_short(self.league)))

    @app_commands.command(description="Get the scoreboard for a given week.")
    async def scoreboard(self, interaction, week: int):
        await interaction.response.send_message(self.codeblock("Week {} ".format(week)+espn.get_scoreboard_short(self.league, week)))

    @app_commands.command(description="Get projected scores for the week.")
    async def projected_scores(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_projected_scoreboard(self.league)))

    @app_commands.command(description="Get current standings.")
    async def standings(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_standings(self.league)))

    @app_commands.command(description="Get players to monitor.")
    async def players_to_monitor(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_monitor(self.league)))

    @app_commands.command(description="Get the week's matchups.")
    async def matchups(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_matchups(self.league)))

    @app_commands.command(description="Get close projected scores for the week.")
    async def close_scores(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_close_scores(self.league)))

    @app_commands.command(description="Get power rankings for the week.")
    async def power_rankings(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_power_rankings(self.league)))

    @app_commands.command(description="Get injury status of a player.")
    async def player_status(self, interaction, player_name: str):
        await interaction.response.send_message(self.codeblock(player_name + " is " + espn.get_player_status(self.league, player_name)))
        
    @app_commands.command(description="Get the lineup for a team.")
    async def lineup(self, interaction, team_name: str, week: int = None):
        await interaction.response.send_message(self.codeblock(espn.get_lineup(self.league, team_name, week)))

    @app_commands.command(description="Get season recap.")
    async def recap(self, interaction):
        await interaction.response.send_message(self.codeblock(recap.trophy_recap(self.league)))

    @app_commands.command(description="Get season win matrix.")
    async def win_matrix(self, interaction):
        await interaction.response.send_message(self.codeblock(recap.win_matrix(self.league)))

    @lineup.autocomplete('team_name')
    async def team_names_autocomplete(self, interaction, current: str):
        team_names = espn.get_team_names(self.league)
        return [app_commands.Choice(name=team_name, value=team_name) for team_name in team_names if current.lower() in team_name.lower()]

    @app_commands.command(description="Is CMC still injured?")
    async def cmc(self, interaction):
        await interaction.response.send_message(self.codeblock(espn.get_cmc_still_injured(self.league)))

    @staticmethod
    def codeblock(string):
        return "```{0}```".format(string)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.copy_global_to(guild=self.guild)
        await self.bot.tree.sync(guild=self.guild)