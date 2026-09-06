import discord
from discord.ext import commands
from discord import app_commands
import gamedaybot.espn.functionality as espn
import gamedaybot.espn.season_recap as recap
import gamedaybot.utils.report as reports
from espn_api.football import League
import logging


class FantasyFootballCog(commands.Cog):
    def __init__(self, bot, league, guild_id):
        self.bot = bot
        self.league = league
        # DISCORD_SERVER_ID is optional; discord.Object(id=None) raises TypeError.
        self.guild = discord.Object(id=guild_id) if guild_id else None

    async def reply(self, interaction, report, empty="Nothing to report right now."):
        """
        Answer a slash command with a rich embed.

        Falls back to the old code block when there is no report, or when the
        content is too large to be a valid embed.
        """
        if report is None:
            await interaction.response.send_message(self.codeblock(empty))
        elif report.fits_embed():
            await interaction.response.send_message(embed=discord.Embed.from_dict(report.to_embed()))
        else:
            await interaction.response.send_message(self.codeblock(report.to_text()))

    async def reply_deferred(self, interaction, report, empty="Nothing to report right now."):
        """As reply(), for commands slow enough to need interaction.response.defer() first."""
        if report is None:
            await interaction.followup.send(self.codeblock(empty))
        elif report.fits_embed():
            await interaction.followup.send(embed=discord.Embed.from_dict(report.to_embed()))
        else:
            await interaction.followup.send(self.codeblock(report.to_text()))

    @app_commands.command(description="Get current scores for the week.")
    async def current_scores(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_scoreboard_short(self.league), color=reports.BLUE))

    @app_commands.command(description="Get the scoreboard for a given week.")
    async def scoreboard(self, interaction, week: int):
        # get_scoreboard_short's own 'Score Update' header is dropped; the title replaces it.
        lines = espn.get_scoreboard_short(self.league, week).split("\n")
        report = reports.Report(title="Week {} Scores".format(week), body=lines[1:],
                                color=reports.BLUE)
        await self.reply(interaction, report)

    @app_commands.command(description="Get projected scores for the week.")
    async def projected_scores(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_projected_scoreboard(self.league), color=reports.GREY))

    @app_commands.command(description="Get current standings.")
    async def standings(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_standings(self.league), color=reports.BLUE))

    @app_commands.command(description="Get the playoff picture and clinching scenarios.")
    async def playoff_picture(self, interaction):
        await self.reply(interaction,
                         reports.from_text(espn.get_playoff_picture(self.league),
                                           color=reports.BLUE),
                         empty="No playoff picture yet - no games have been played.")

    @app_commands.command(description="Get draft grades plus the biggest steals and busts.")
    async def draft_report(self, interaction):
        # Grading pulls season points for every drafted player, so this is slow.
        await interaction.response.defer()
        await self.reply_deferred(interaction,
                                  reports.from_text(espn.get_draft_report(self.league),
                                                    color=reports.ORANGE),
                                  empty="No draft data available for this league.")

    @app_commands.command(description="Get players to monitor.")
    async def players_to_monitor(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_monitor(self.league), color=reports.RED))

    @app_commands.command(description="Get the week's matchups.")
    async def matchups(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_matchups(self.league), color=reports.BLUE))

    @app_commands.command(description="Get close projected scores for the week.")
    async def close_scores(self, interaction):
        await self.reply(interaction,
                         reports.from_text(espn.get_close_scores(self.league),
                                           color=reports.ORANGE),
                         empty="No close scores this week.")

    @app_commands.command(description="Get power rankings for the week.")
    async def power_rankings(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_power_rankings(self.league), color=reports.PURPLE))

    @app_commands.command(description="Get the trophies for the week.")
    async def trophies(self, interaction):
        week = espn.last_completed_week(self.league)
        fields = espn.trophy_fields(self.league, week=week)
        report = reports.Report(title='Trophies of the week:', fields=fields,
                                color=reports.GOLD, footer='Week {}'.format(week)) if fields else None
        await self.reply(interaction, report, empty="No trophies to hand out this week.")

    @app_commands.command(description="Get injury status of a player.")
    async def player_status(self, interaction, player_name: str):
        status = espn.get_player_status(self.league, player_name)
        await self.reply(interaction, reports.Report(
            title="Injury Report", fields=[(player_name, status, False)], color=reports.RED))

    @app_commands.command(description="Get the lineup for a team.")
    async def lineup(self, interaction, team_name: str, week: int = None):
        await self.reply(interaction, reports.from_text(
            espn.get_lineup(self.league, team_name, week), color=reports.BLUE))

    @app_commands.command(description="Get season recap.")
    async def recap(self, interaction):
        await interaction.response.defer()
        await self.reply_deferred(interaction, reports.from_text(
            recap.trophy_recap(self.league), color=reports.GOLD))

    @app_commands.command(description="Get season win matrix.")
    async def win_matrix(self, interaction):
        await interaction.response.defer()
        await self.reply_deferred(interaction, reports.from_text(
            recap.win_matrix(self.league), color=reports.PURPLE))

    @lineup.autocomplete('team_name')
    async def team_names_autocomplete(self, interaction, current: str):
        team_names = espn.get_team_names(self.league)
        return [app_commands.Choice(name=team_name, value=team_name) for team_name in team_names if current.lower() in team_name.lower()]

    @app_commands.command(description="Is CMC still injured?")
    async def cmc(self, interaction):
        await self.reply(interaction, reports.from_text(
            espn.get_cmc_still_injured(self.league), color=reports.RED))

    @staticmethod
    def codeblock(string):
        return "```{0}```".format(string)

    @commands.Cog.listener()
    async def on_ready(self):
        if self.guild is None:
            # No guild configured: sync globally instead of crashing on startup.
            await self.bot.tree.sync()
            return
        self.bot.tree.copy_global_to(guild=self.guild)
        await self.bot.tree.sync(guild=self.guild)
