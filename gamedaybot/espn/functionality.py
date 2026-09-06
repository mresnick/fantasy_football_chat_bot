from datetime import date
from datetime import datetime
from datetime import timedelta
import functools
import random


def get_scoreboard_short(league, week=None):
    """
    Retrieve the scoreboard for a given week of the fantasy football season.

    Parameters
    ----------
    league: espn_api.football.League
        The league for which to retrieve the scoreboard.
    week: int
        The week of the season for which to retrieve the scoreboard.

    Returns
    -------
    list of dict
        A list of dictionaries representing the games on the scoreboard for the given week. Each dictionary contains
        information about a single game, including the teams and their scores.
    """

    # Gets current week's scoreboard
    box_scores = league.box_scores(week=week)
    score = ['%4s %6.2f - %6.2f %s' % (i.home_team.team_abbrev, i.home_score,
                                       i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)


def get_projected_scoreboard(league, week=None):
    """
    Retrieve the projected scoreboard for a given week of the fantasy football season.

    Parameters
    ----------
    league: espn_api.football.League
        The league for which to retrieve the projected scoreboard.
    week: int
        The week of the season for which to retrieve the projected scoreboard.

    Returns
    -------
    list of dict
        A list of dictionaries representing the projected games on the scoreboard for the given week. Each dictionary
        contains information about a single game, including the teams and their projected scores.
    """

    # Gets current week's scoreboard projections
    box_scores = league.box_scores(week=week)
    score = ['%4s %6.2f - %6.2f %s' % (i.home_team.team_abbrev, i.home_projected,
                                       i.away_projected, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Approximate Projected Scores'] + score
    return '\n'.join(text)


def get_standings(league, top_half_scoring=False, week=None):
    """
    Retrieve the current standings for a fantasy football league, with an option to include top-half scoring.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the standings.
    top_half_scoring: bool, optional
        If True, include top-half scoring in the standings calculation. Defaults to False.
    week: int, optional
        The week for which to retrieve the standings. Defaults to the current week of the league.

    Returns
    -------
    str
        A string containing the current standings, formatted as a list of teams with their records and positions.
    """

    standings_txt = ''
    teams = league.teams
    standings = []
    if not top_half_scoring:
        standings = league.standings()
        standings_txt = [f"{pos + 1:2}: ({team.wins}-{team.losses}) {team.team_name} " for
                         pos, team in enumerate(standings)]
    else:
        # top half scoring can be enabled by default in ESPN now.
        # this should generally not be used
        top_half_totals = {t.team_name: 0 for t in teams}
        if not week:
            week = league.current_week
        for w in range(1, week):
            top_half_totals = top_half_wins(league, top_half_totals, w)

        for t in teams:
            wins = top_half_totals[t.team_name] + t.wins
            standings.append((wins, t.losses, t.team_name))

        standings = sorted(standings, key=lambda tup: tup[0], reverse=True)
        standings_txt = [f"{pos + 1:2}: {team_name} ({wins}-{losses}) (+{top_half_totals[team_name]})" for
                         pos, (wins, losses, team_name) in enumerate(standings)]
    text = ["Current Standings"] + standings_txt

    return "\n".join(text)


def top_half_wins(league, top_half_totals, week):
    box_scores = league.box_scores(week=week)

    scores = [(i.home_score, i.home_team.team_name) for i in box_scores] + \
        [(i.away_score, i.away_team.team_name) for i in box_scores if i.away_team]

    scores = sorted(scores, key=lambda tup: tup[0], reverse=True)

    for i in range(0, len(scores) // 2):
        points, team_name = scores[i]
        top_half_totals[team_name] += 1

    return top_half_totals


def last_completed_week(league):
    """
    Return the week whose games have finished, i.e. the week a Tuesday recap should report on.

    league.current_week cannot be used for this. espn_api clamps current_week to
    finalScoringPeriod, so once the season ends it stops advancing and
    `current_week - 1` points at the second-to-last week forever. scoringPeriodId
    is not clamped, so it still rolls over to (last week + 1) after the final week.

    Parameters
    ----------
    league: object
        The league object for which to determine the last completed week.

    Returns
    -------
    int
        The most recently completed week, clamped to the league's final matchup week.
    """

    last_matchup_week = len(league.settings.matchup_periods)
    # scoringPeriodId is the week now in progress; the one before it just finished.
    week = min(league.scoringPeriodId, last_matchup_week + 1) - 1
    return max(week, 1)


def all_played(lineup):
    """
    Check if all the players in a given lineup have played their game.

    Parameters
    ----------
    lineup : list
        A list of player objects that represents the lineup

    Returns
    -------
    bool
        True if all the players in the lineup have played their game, False otherwise.
    """

    for i in lineup:
        # exclude player on bench and injured reserve
        if i.slot_position != 'BE' and i.slot_position != 'IR' and i.game_played < 100:
            return False
    return True


def get_monitor(league):
    """
    Retrieve a list of players from a given fantasy football league that should be monitored during a game.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the monitor players.

    Returns
    -------
    str
        A string containing the list of players to monitor, formatted as a list of player names and status.
    """

    box_scores = league.box_scores()
    monitor = []
    text = ''
    for i in box_scores:
        monitor += scan_roster(i.home_lineup, i.home_team)
        monitor += scan_roster(i.away_lineup, i.away_team)

    if monitor:
        text = ['Starting Players to Monitor'] + monitor
    else:
        text = ['No Players to Monitor this week. Good Luck!']
    return '\n'.join(text)


def scan_roster(lineup, team):
    """
    Retrieve a list of players from a given fantasy football league that have a status.

    Parameters
    ----------
    lineup : list
        A list of player objects that represents the lineup
    team : object
        The team object for which to retrieve the monitor players

    Returns
    -------
    list
        A list of strings containing the list of players to monitor, formatted as a list of player names and statuses.
    """

    count = 0
    players = []
    for i in lineup:
        # exclude bench and injured players and active or normal players
        if i.slot_position != 'BE' and i.slot_position != 'IR' and \
            i.injuryStatus != 'ACTIVE' and i.injuryStatus != 'NORMAL' \
                and i.game_played == 0:

            count += 1
            player = i.position + ' ' + i.name + ' - ' + i.injuryStatus.title().replace('_', ' ')
            players += [player]

        if i.slot_position == 'IR' and \
            i.injuryStatus != 'INJURY_RESERVE' and i.injuryStatus != 'OUT':

            count += 1
            player = i.position + ' ' + i.name + ' - Not IR eligible'
            players += [player]

    list = ""
    report = ""

    for p in players:
        list += p + "\n"

    if count > 0:
        s = '%s: \n%s \n' % (team.team_name, list[:-1])
        report = [s.lstrip()]

    return report


def get_matchups(league, week=None):
    """
    Retrieve the matchups for a given week in a fantasy football league.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the matchups.
    week : int, optional
        The week number for which to retrieve the matchups, by default None.

    Returns
    -------
    str
        A string containing the matchups for the given week, formatted as a list of team names and abbreviation.
    """

    # Gets current week's Matchups
    matchups = league.box_scores(week=week)

    full_names = ['%s vs %s' % (i.home_team.team_name, i.away_team.team_name) for i in matchups if i.away_team]

    abbrevs = ['%4s (%s-%s) vs (%s-%s) %s' % (i.home_team.team_abbrev, i.home_team.wins, i.home_team.losses,
                                              i.away_team.wins, i.away_team.losses, i.away_team.team_abbrev) for i in matchups
               if i.away_team]

    text = ['Matchups'] + full_names + [''] + abbrevs
    return '\n'.join(text)


def get_close_scores(league, week=None):
    """
    Retrieve the projected closest scores (15 points or closer) for a given week in a fantasy football league.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the closest scores.
    week : int, optional
        The week number for which to retrieve the closest scores, by default None.

    Returns
    -------
    str
        A string containing the projected closest scores for the given week, formatted as a list of team names and abbreviation.
    """

    # Gets current projected closest scores (15 points or closer)
    box_scores = league.box_scores(week=week)
    score = []

    for i in box_scores:
        if i.away_team:
            away_projected = i.away_projected
            home_projected = i.home_projected
            diffScore = away_projected - home_projected

            if (abs(diffScore) <= 15 and (not all_played(i.away_lineup) or not all_played(i.home_lineup))):
                score += ['%4s %6.2f - %6.2f %s' % (i.home_team.team_abbrev, i.home_projected,
                                                    i.away_projected, i.away_team.team_abbrev)]

    if not score:
        return ('')
    text = ['Projected Close Scores'] + score
    return '\n'.join(text)

@functools.total_ordering
class OrderedBoxPlayer():
    order = ['QB', 'RB', 'WR', 'TE', 'RB/WR/TE', 'D/ST', 'K', 'BE', 'IR']
    def __init__(self, box_player):
        self.box_player = box_player

    def __lt__(self, other):
        return self.__class__.order.index(self.box_player.slot_position) < self.__class__.order.index(other.box_player.slot_position)

    def __eq__(self, other):
        return self.box_player.slot_position == other.box_player.slot_position

def get_lineup(league, team_name, week=None):
    box_scores = league.box_scores(week=week)
    lineup = []
    for i in box_scores:
        if i.home_team.team_name == team_name:
            lineup = i.home_lineup
            break
        elif i.away_team.team_name == team_name:
            lineup = i.away_lineup
            break

    lineup = [OrderedBoxPlayer(p) for p in lineup]
    lineup.sort()

    for player in lineup:
        if player.box_player.slot_position == "RB/WR/TE":
            player.box_player.slot_position = "FLEX"

        if player.box_player.on_bye_week == True:
            player.box_player.points = "BYE"

        if player.box_player.game_played == 0:
            player.box_player.points = "N/A"

    title = team_name + " Roster"
    if week != None: title = title + " Week " + str(week)
    return title + "\n" + "\n".join([("{:20}" + ("("+p.box_player.injuryStatus[0]+")" if p.box_player.injuryStatus[0] not in ('A','N') else "   ") + " - {:4} - " + ("{:>6.2f}" if isinstance(p.box_player.points, float) else "{:>6}")).format(p.box_player.name, p.box_player.slot_position.replace("RB/WR/TE", "FLEX"), p.box_player.points) for p in lineup])

def get_team_names(league):
    return [t.team_name for t in league.teams]

def get_waiver_report(league, faab=False):
    """
    This function generates a waiver report for a given league.
    The report lists all the waiver transactions that occurred on the current day,
    including the team that made the transaction, the player added and the player dropped (if applicable).

    Parameters
    ----------
    league: object
        The league object for which the report is being generated
    faab : bool, optional
        A flag to indicate whether the report should include FAAB amount spent, by default False.

    Returns
    -------
    str
        A string containing the waiver report
    """

    # Get the recent activity of the league
    activities = league.recent_activity(50)
    # Initialize an empty list to store the report
    report = []
    # Get the current date
    today = date.today().strftime('%Y-%m-%d')
    text = ''

    # Iterate through each activity
    for activity in activities:
        actions = activity.actions
        # Get the date of the activity
        d2 = date.fromtimestamp(activity.date / 1000).strftime('%Y-%m-%d')
        # Check if the activity is from today
        if d2 == today:
            # Check if the activity is a waiver add (not a drop)
            if len(actions) == 1 and actions[0][1] == 'WAIVER ADDED':
                # Get the team, player name and position
                team_name = actions[0][0].team_name
                player_name = actions[0][2].name
                player_position = actions[0][2].position
                if faab:
                    # Get the FAAB amount spent
                    faab_amount = actions[0][3]
                    # Add the transaction to the report
                    s = f'{team_name} \nADDED {player_position} {player_name} (${faab_amount})\n'
                else:
                    s = f'{team_name} \nADDED {player_position} {player_name}\n'
                report += [s.lstrip()]
            elif len(actions) > 1:
                if actions[0][1] == 'WAIVER ADDED' or actions[1][1] == 'WAIVER ADDED':
                    if actions[0][1] == 'WAIVER ADDED':
                        if faab:
                            s = '%s \nADDED %s %s ($%s)\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[0][2].position, actions[0][2].name,
                                actions[0][3], actions[1][2].position, actions[1][2].name)
                        else:
                            s = '%s \nADDED %s %s\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[0][2].position, actions[0][2].name,
                                actions[1][2].position, actions[1][2].name)
                    else:
                        if faab:
                            s = '%s \nADDED %s %s ($%s)\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[1][2].position, actions[1][2].name,
                                actions[1][3], actions[0][2].position, actions[0][2].name)
                        else:
                            s = '%s \nADDED %s %s\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[1][2].position, actions[1][2].name,
                                actions[0][2].position, actions[0][2].name)
                    report += [s.lstrip()]

    report.reverse()

    if not report:
        text = ['No waiver transactions']
    else:
        text = ['Waiver Report %s: ' % today] + report

    return '\n'.join(text)


def get_power_rankings(league, week=None):
    """
    This function returns the power rankings of the teams in the league for a specific week,
    along with the change in power ranking number and playoff percentage from the previous week.
    If the week is not provided, it defaults to the current week.
    The power rankings are determined using a 2 step dominance algorithm,
    as well as a combination of points scored and margin of victory.
    It's weighted 80/15/5 respectively.

    Parameters
    ----------
    league: object
        The league object for which the power rankings are being generated
    week : int, optional
        The week for which the power rankings are to be returned (default is current week)

    Returns
    -------
    str
        A string representing the power rankings with changes from the previous week
    """

    # Check if the week is provided, if not use the previous week
    if not week:
        week = league.current_week - 1

    p_rank_up_emoji = "🟢"
    p_rank_down_emoji = "🔻"
    p_rank_same_emoji = "🟰"

    # Get the power rankings for the previous 2 weeks
    week = max(week, 1)
    current_rankings = league.power_rankings(week=week)
    previous_rankings = league.power_rankings(week=week - 1) if week > 1 else []

    # Normalize the scores
    def normalize_rankings(rankings):
        if not rankings:
            return []
        max_score = max(float(score) for score, _ in rankings)
        if max_score == 0:
            # Nothing has been scored yet (e.g. before week 1 games finish).
            return [("0.00", team) for _, team in rankings]
        return [(f"{99.99 * float(score) / max_score:.2f}", team) for score, team in rankings]


    normalized_current_rankings = normalize_rankings(current_rankings)
    normalized_previous_rankings = normalize_rankings(previous_rankings)

    # Convert normalized previous rankings to a dictionary for easy lookup
    previous_rankings_dict = {team.team_abbrev: score for score, team in normalized_previous_rankings}

    # Prepare the output string
    rankings_text = ['Power Rankings (Playoff %)']
    for normalized_current_score, current_team in normalized_current_rankings:
        team_abbrev = current_team.team_abbrev
        rank_change_text = ''

        # Check if the team was present in the normalized previous rankings
        if team_abbrev in previous_rankings_dict:
            previous_score = float(previous_rankings_dict[team_abbrev])
            if previous_score != 0:
                rank_change_percent = ((float(normalized_current_score) - previous_score) / previous_score) * 100
                rank_change_emoji = p_rank_up_emoji if rank_change_percent > 0 else p_rank_down_emoji if rank_change_percent < 0 else p_rank_same_emoji
                rank_change_text = f"[{rank_change_emoji}{abs(rank_change_percent):4.1f}%]"

        rankings_text.append(f"{normalized_current_score}{rank_change_text} ({current_team.playoff_pct:4.1f}) - {team_abbrev}")

    return '\n'.join(rankings_text)


def get_starter_counts(league):
    """
    Get the number of starters for each position

    Parameters
    ----------
    league : object
        The league object for which the starter counts are being generated

    Returns
    -------
    dict
        A dictionary containing the number of players at each position within the starting lineup.
    """

    # Read the slot counts straight from league settings. Deriving them from a
    # box score breaks whenever that week's rosters are on bye or were never set,
    # and returned None when every lineup was empty.
    return {pos: count for pos, count in league.settings.position_slot_counts.items()
            if pos not in ('BE', 'IR') and count != 0}


def best_flex(flexes, player_pool, num):
    """
    Given a list of flex positions, a dictionary of player pool, and a number of players to return,
    this function returns the best flex players from the player pool.

    Parameters
    ----------
    flexes : list
        a list of strings representing the flex positions
    player_pool : dict
        a dictionary with keys as position and values as a dictionary with player name as key and value as score
    num : int
        number of players to return from the player pool

    Returns
    ----------
    best : dict
        a dictionary containing the best flex players from the player pool
    player_pool : dict
        the updated player pool after removing the best flex players
    """

    pool = {}
    # iterate through each flex position
    for flex_position in flexes:
        # add players from flex position to the pool
        try:
            pool = pool | player_pool[flex_position]
        except KeyError:
            pass
    # sort the pool by score in descending order
    pool = {k: v for k, v in sorted(pool.items(), key=lambda item: item[1], reverse=True)}
    # get the top num players from the pool
    best = dict(list(pool.items())[:num])
    # remove the best flex players from the player pool
    for pos in player_pool:
        for p in best:
            if p in player_pool[pos]:
                player_pool[pos].pop(p)
    return best, player_pool


def optimal_lineup_score(lineup, starter_counts):
    """
    This function returns the optimal lineup score based on the provided lineup and starter counts.

    Parameters
    ----------
    lineup : list
        A list of player objects for which the optimal lineup score is being generated
    starter_counts : dict
        A dictionary containing the number of starters for each position

    Returns
    -------
    tuple
        A tuple containing the optimal lineup score, the provided lineup score, the difference between the two scores,
        and the percentage of the provided lineup's score compared to the optimal lineup's score.
    """

    best_lineup = {}
    position_players = {}

    # get all players and points
    score = 0
    score_pct = 0
    best_score = 0

    for player in lineup:
        try:
            position_players[player.position][player.name] = player.points
        except KeyError:
            position_players[player.position] = {}
            position_players[player.position][player.name] = player.points
        if player.slot_position not in ['BE', 'IR']:
            score += player.points

    # sort players by position for points
    for position in starter_counts:
        try:
            position_players[position] = {k: v for k, v in sorted(
                position_players[position].items(), key=lambda item: item[1], reverse=True)}
            best_lineup[position] = dict(list(position_players[position].items())[:starter_counts[position]])
            position_players[position] = dict(list(position_players[position].items())[starter_counts[position]:])
        except KeyError:
            best_lineup[position] = {}

    # flexes. need to figure out best in other single positions first
    for position in starter_counts:
        # flex
        if 'D/ST' not in position and '/' in position:
            flex = position.split('/')
            result = best_flex(flex, position_players, starter_counts[position])
            best_lineup[position] = result[0]
            position_players = result[1]

    # Offensive Player. need to figure out best in other positions first
    if 'OP' in starter_counts:
        flex = ['RB', 'WR', 'TE', 'QB']
        result = best_flex(flex, position_players, starter_counts['OP'])
        best_lineup['OP'] = result[0]
        position_players = result[1]

    # Defensive Player. need to figure out best in other positions first
    if 'DP' in starter_counts:
        flex = ['DT', 'DE', 'LB', 'CB', 'S']
        result = best_flex(flex, position_players, starter_counts['DP'])
        best_lineup['DP'] = result[0]
        position_players = result[1]

    for position in best_lineup:
        best_score += sum(best_lineup[position].values())

    if best_score != 0:
        score_pct = (score / best_score) * 100

    return (best_score, score, best_score - score, score_pct)


def optimal_team_scores(league, week=None, full_report=False, recap=False):
    """
    This function returns the optimal team scores or managers.

    Parameters
    ----------
    league : object
        The league object for which the optimal team scores are being generated
    week : int, optional
        The week for which the optimal team scores are to be returned (default is the previous week)
    full_report : bool, optional
        A boolean indicating if a full report should be returned (default is False)

    Returns
    -------
    str or tuple
        If full_report is True, a string representing the full report of the optimal team scores.
        If full_report is False, a tuple containing the best and worst manager strings.
    """

    if not week:
        week = league.current_week - 1
    box_scores = league.box_scores(week=week)
    results = []
    best_scores = {}
    starter_counts = get_starter_counts(league)

    for i in box_scores:
        if i.home_team != 0:
            best_scores[i.home_team] = optimal_lineup_score(i.home_lineup, starter_counts)
        if i.away_team != 0:
            best_scores[i.away_team] = optimal_lineup_score(i.away_lineup, starter_counts)

    best_scores = {key: value for key, value in sorted(best_scores.items(), key=lambda item: item[1][3], reverse=True)}

    if full_report:
        i = 1
        for score in best_scores:
            s = ['%2d: %4s: %6.2f (%6.2f - %.2f%%)' %
                 (i, score.team_abbrev, best_scores[score][0],
                  best_scores[score][1], best_scores[score][3])]
            results += s
            i += 1

        text = ['Optimal Scores:  (Actual - % of optimal)'] + results
        return '\n'.join(text)
    else:
        num_teams = 0
        team_names = ''
        for score in best_scores:
            if best_scores[score][3] > 99.8:
                num_teams += 1
                team_names += score.team_name + ', '
            else:
                break

        if num_teams <= 1:
            best = next(iter(best_scores.items()))
            best_mgr_str = ['🤖 Best Manager 🤖'] + ['%s scored %.2f%% of their optimal score!' % (best[0].team_name, best[1][3])]
        else:
            team_names = team_names[:-2]
            best_mgr_str = ['🤖 Best Managers 🤖'] + [f'{team_names} scored their optimal score!']

        worst = best_scores.popitem()
        if recap:
            return worst[0].team_abbrev

        worst_mgr_str = ['🤡 Worst Manager 🤡'] + ['%s left %.2f points on their bench. Only scoring %.2f%% of their optimal score.' %
                                                 (worst[0].team_name, worst[1][0] - worst[1][1], worst[1][3])]

        return (best_mgr_str + worst_mgr_str)


def get_most_active_and_laziest(league, week=None, recap=False):
    if not week:
        week = league.current_week - 1

    teams = league.teams

    first_game_date = league.espn_request.get_pro_schedule()['settings']['playerOwnershipSettings']['firstGameDate']
    week_1_start_date = (datetime.fromtimestamp(first_game_date/1000) - timedelta(days=2)).replace(hour=7, minute=30, second=0, microsecond=0)

    start_timestamp = datetime.timestamp(week_1_start_date + timedelta(weeks=(week - 1))) * 1000
    end_timestamp = datetime.timestamp(week_1_start_date + timedelta(weeks=week)) * 1000

    most_moves = 0
    fewest_moves = 999

    most_active = []
    laziest = []

    adds = {}
    drops = {}
    trades = {}

    for team in teams:
        adds[team] = 0
        drops[team] = 0
        trades[team] = 0

    recent_activity = league.recent_activity(999)


    for activity in recent_activity:
        if activity.date > start_timestamp and activity.date < end_timestamp:
             for action in activity.actions:
                    team = action[0]
                    action_type = action[1]
                    if action_type in ('FA ADDED', 'WAIVER ADDED'):
                        adds[team] = adds[team] + 1
                    elif action_type == 'DROPPED':
                        drops[team] = drops[team] + 1
                    elif action_type == 'TRADED':
                        trades[team] = trades[team] + 1

    for team in teams:
        total = adds[team] + drops[team] + trades[team]
        if total > most_moves:
            most_moves = total
            most_active = [team]
        elif total == most_moves:
            most_active.append(team)
        if total < fewest_moves:
            fewest_moves = total
            laziest = [team]
        elif total == fewest_moves:
            laziest.append(team)

    if recap:
        return [team.team_abbrev for team in most_active], [team.team_abbrev for team in laziest]

    most_active_prefix = ['🤯 Most Active Manager 🤯']
    laziest_prefix = ['😴 Laziest Manager 😴']

    if len(most_active) == 1:
        most_active_team_name = most_active[0].team_name
        most_active_str = most_active_prefix + ['%s had %s adds, %s drops, and %s trades!' % (most_active_team_name, adds[most_active[0]], drops[most_active[0]], trades[most_active[0]])]
    else:
        most_active_str = most_active_prefix + ['%s were tied with %s moves!' % (", ".join([team.team_name for team in most_active]), most_moves)]

    if len(laziest) == 1:
        laziest_team_name = laziest[0].team_name
        laziest_str = laziest_prefix + ['%s had %s adds, %s drops, and %s trades!' % (laziest_team_name, adds[laziest[0]], drops[laziest[0]], trades[laziest[0]])]
    else:
        laziest_str = laziest_prefix + ['%s were tied with %s moves!' % (", ".join([team.team_name for team in laziest]), fewest_moves)]

    return (most_active_str + laziest_str)


def get_achievers_trophy(league, week=None, recap=False):
    """
    This function returns the overachiever and underachiever of the league
    based on the difference between the projected score and the actual score.

    Parameters
    ----------
    league: object
        The league object for which the overachiever and underachiever are being determined
    week : int, optional
        The week for which the overachiever and underachiever are to be returned (default is current week)

    Returns
    -------
    str
        A string representing the overachiever and underachiever of the league
    """

    box_scores = league.box_scores(week=week)
    high_achiever_str = ['📈 Overachiever 📈']
    low_achiever_str = ['📉 Underachiever 📉']
    best_performance = -9999
    worst_performance = 9999
    for i in box_scores:
        home_performance = i.home_score - i.home_projected
        away_performance = i.away_score - i.away_projected

        if i.home_team != 0:
            if home_performance > best_performance:
                best_performance = home_performance
                over_achiever = i.home_team
            if home_performance < worst_performance:
                worst_performance = home_performance
                under_achiever = i.home_team
        if i.away_team != 0:
            if away_performance > best_performance:
                best_performance = away_performance
                over_achiever = i.away_team
            if away_performance < worst_performance:
                worst_performance = away_performance
                under_achiever = i.away_team

    if recap:
        return over_achiever.team_abbrev, under_achiever.team_abbrev

    if best_performance > 0:
        high_achiever_str += ['%s was %.2f points over their projection' % (over_achiever.team_name, best_performance)]
    else:
        high_achiever_str += ['No team out performed their projection']

    if worst_performance < 0:
        low_achiever_str += ['%s was %.2f points under their projection' % (under_achiever.team_name, abs(worst_performance))]
    else:
        low_achiever_str += ['No team was worse than their projection']

    return (high_achiever_str + low_achiever_str)


def get_weekly_score_with_win_loss(league, week=None):
    box_scores = league.box_scores(week=week)
    weekly_scores = {}
    for i in box_scores:
        if i.home_team != 0 and i.away_team != 0:
            if i.home_score > i.away_score:
                weekly_scores[i.home_team] = [i.home_score, 'W']
                weekly_scores[i.away_team] = [i.away_score, 'L']
            else:
                weekly_scores[i.home_team] = [i.home_score, 'L']
                weekly_scores[i.away_team] = [i.away_score, 'W']
    return dict(sorted(weekly_scores.items(), key=lambda item: item[1], reverse=True))


def get_lucky_trophy(league, week=None, recap=False):
    """
    This function takes in a league object and an optional week parameter. It retrieves the box scores for the specified league and week, and creates a dictionary with the weekly scores for each team. The teams are sorted in descending order by their scores, and the team with the lowest score and won is determined to be the lucky team for the week. The team with the highest score and lost is determined to be the unlucky team for the week. The function returns a list containing the lucky and unlucky teams, along with their records for the week.
    Parameters:
    league (object): A league object containing information about the league and its teams.
    week (int, optional): The week for which the box scores should be retrieved. If no week is specified, the current week will be used.
    Returns:
    list: A list containing the lucky and unlucky teams, along with their records for the week.
    """
    weekly_scores = get_weekly_score_with_win_loss(league, week=week)
    losses = 0
    unlucky_record = ''
    lucky_record = ''
    num_teams = len(weekly_scores) - 1

    for t in weekly_scores:
        if weekly_scores[t][1] == 'L':
            unlucky_team = t
            unlucky_record = str(num_teams - losses) + '-' + str(losses)
            break
        losses += 1

    wins = 0
    weekly_scores = dict(sorted(weekly_scores.items(), key=lambda item: item[1]))
    for t in weekly_scores:
        if weekly_scores[t][1] == 'W':
            lucky_team = t
            lucky_record = str(wins) + '-' + str(num_teams - wins)
            break
        wins += 1

    if recap:
        return lucky_team.team_abbrev, unlucky_team.team_abbrev, weekly_scores

    lucky_str = ['🍀 Lucky 🍀']+['%s was %s against the league, but still got the win' % (lucky_team.team_name, lucky_record)]
    unlucky_str = ['😡 Unlucky 😡']+['%s was %s against the league, but still took an L' % (unlucky_team.team_name, unlucky_record)]
    return (lucky_str + unlucky_str)


def week_extremes(league, week):
    """
    Scan a week's box scores for the high, low, blowout and closest games.

    Shared by get_trophies and trophy_fields so the scan (and its box_scores
    request) happens once per report rather than once per rendering.

    Parameters
    ----------
    league : object
        The league object to scan.
    week : int
        The week to scan.

    Returns
    -------
    dict or None
        Teams and margins for the week, or None if no matchups were scored
        (an empty schedule, or every team on a bye).
    """

    matchups = league.box_scores(week=week)
    low_score = 99999999
    high_score = -1
    closest_score = 99999999
    biggest_blowout = -1
    high_team = low_team = None
    close_winner = close_loser = None
    ownerer = blown_out = None

    for i in matchups:
        if i.home_team != 0:
            if i.home_score > high_score:
                high_score = i.home_score
                high_team = i.home_team
            if i.home_score < low_score:
                low_score = i.home_score
                low_team = i.home_team
        if i.away_team != 0:
            if i.away_score > high_score:
                high_score = i.away_score
                high_team = i.away_team
            if i.away_score < low_score:
                low_score = i.away_score
                low_team = i.away_team

        if i.away_team != 0 and i.home_team != 0:
            if i.away_score - i.home_score != 0 and \
                    abs(i.away_score - i.home_score) < closest_score:
                closest_score = abs(i.away_score - i.home_score)
                if i.away_score - i.home_score < 0:
                    close_winner = i.home_team
                    close_loser = i.away_team
                else:
                    close_winner = i.away_team
                    close_loser = i.home_team
            if abs(i.away_score - i.home_score) > biggest_blowout:
                biggest_blowout = abs(i.away_score - i.home_score)
                if i.away_score - i.home_score < 0:
                    ownerer = i.home_team
                    blown_out = i.away_team
                else:
                    ownerer = i.away_team
                    blown_out = i.home_team

    if high_team is None:
        return None

    return {
        'high_team': high_team, 'high_score': high_score,
        'low_team': low_team, 'low_score': low_score,
        'ownerer': ownerer, 'blown_out': blown_out, 'biggest_blowout': biggest_blowout,
        'close_winner': close_winner, 'close_loser': close_loser, 'closest_score': closest_score,
    }


def trophy_fields(league, week=None):
    """
    Every trophy for a week as (label, value) pairs.

    The structured form of get_trophies: identical content, not yet joined into
    a string, so it can become Discord embed fields as well as text.

    Parameters
    ----------
    league : object
        The league object for which the trophies are generated.
    week : int, optional
        The week to report on, defaults to the previously completed week.

    Returns
    -------
    list
        (label, value) pairs, empty if the week had no scored matchups.
    """

    if not week:
        week = league.current_week - 1

    extremes = week_extremes(league, week)
    if extremes is None:
        return []

    pairs = [
        ('👑 High score 👑',
         '%s with %.2f points' % (extremes['high_team'].team_name, extremes['high_score'])),
        ('💩 Low score 💩',
         '%s with %.2f points' % (extremes['low_team'].team_name, extremes['low_score'])),
    ]

    # A week can lack a blowout or a close game (e.g. a single matchup, or all ties).
    if extremes['ownerer'] is not None:
        pairs.append(('😱 Blow out 😱', '%s blew out %s by %.2f points' % (
            extremes['ownerer'].team_name, extremes['blown_out'].team_name,
            extremes['biggest_blowout'])))
    if extremes['close_winner'] is not None:
        pairs.append(('😅 Close win 😅', '%s barely beat %s by %.2f points' % (
            extremes['close_winner'].team_name, extremes['close_loser'].team_name,
            extremes['closest_score'])))

    # These each return a flat list of alternating label and value lines.
    flat = (get_lucky_trophy(league, week) + get_achievers_trophy(league, week) +
            optimal_team_scores(league, week) + get_most_active_and_laziest(league, week))
    pairs += list(zip(flat[0::2], flat[1::2]))

    return pairs


def get_trophies(league, week=None, recap=False):
    """
    Returns trophies for the highest score, lowest score, closest score, and biggest win.

    Parameters
    ----------
    league : object
        The league object for which the trophies are to be returned
    week : int, optional
        The week for which the trophies are to be returned (default is current week)
    recap : bool, optional
        Return team abbreviations instead of a message, for the season recap.

    Returns
    -------
    str
        A string representing the trophies
    """
    if not week:
        week = league.current_week - 1

    if recap:
        extremes = week_extremes(league, week)
        if extremes is None:
            return (None, None, None, None)
        return (extremes['high_team'].team_abbrev, extremes['low_team'].team_abbrev,
                extremes['blown_out'].team_abbrev, extremes['close_winner'].team_abbrev)

    pairs = trophy_fields(league, week)
    if not pairs:
        return 'No trophies to hand out this week.'

    text = ['Trophies of the week:']
    for name, value in pairs:
        text += [name, value]
    return '\n'.join(text)


def get_player_status(league, player_name):
    player = league.player_info(name = player_name)
    if player is None:
        return "not found in the league"
    return player.injuryStatus

def get_cmc_still_injured(league):
    injuryStatus = get_player_status(league, "Christian McCaffrey")
    if injuryStatus in ('INJURY_RESERVE', 'OUT'):
        answer = "Yes!"
    elif injuryStatus in('QUESTIONABLE', 'DOUBTFUL'):
        answer = "Probably!"
    else:
        answer = "NO!!!!!!!!!!!! (but check the bot for bugs)"

    return "\n".join(["Is CMC still injured?", answer])


def get_draft_reminder(league, draft_date=None):
    """
    Generate a draft reminder message using ESPN API data or fallback to provided date.
    
    Parameters
    ----------
    league : object
        The league object containing league information
    draft_date : str, optional
        The draft date in format 'YYYY-MM-DD' (fallback if ESPN API doesn't have date)
    
    Returns
    -------
    str
        A formatted draft reminder message
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"get_draft_reminder called with draft_date={draft_date}")
    # Fallback to manual draft date if provided (prioritize this for testing)
    if draft_date:
        try:
            draft_datetime = datetime.strptime(draft_date, '%Y-%m-%d').date()
            today = date.today()
            days_until_draft = (draft_datetime - today).days
            
            if days_until_draft < -1:
                logger.info(f"Draft was {abs(days_until_draft)} days ago - not sending any message")
                return ""  # Don't send any message more than 1 day after draft date passes
            elif days_until_draft == -1:
                logger.info("Draft was yesterday - sending completion message")
                return "✅ DRAFT COMPLETED! ✅\nYour draft was yesterday. Good luck this season!"
            elif days_until_draft == 0:
                logger.info("Draft is today - sending draft day message")
                return "🏈 DRAFT DAY IS TODAY! 🏈\nGet ready to draft your championship team!"
            elif days_until_draft == 1:
                logger.info("Draft is tomorrow - sending tomorrow message")
                return "🔥 DRAFT IS TOMORROW! 🔥\nFinal preparations time - do your research!"
            elif days_until_draft <= 7:
                logger.info(f"Draft is {days_until_draft} days away - sending weekly reminder")
                return f"⏰ DRAFT REMINDER ⏰\n{days_until_draft} days until the draft!\nTime to start your research and rankings!"
            else:
                logger.info(f"Draft is {days_until_draft} days away - sending general reminder")
                return f"📅 DRAFT REMINDER 📅\n{days_until_draft} days until the draft on {draft_date}!\nStart planning your strategy!"
        except ValueError:
            return "Invalid draft date format. Please use YYYY-MM-DD format."
    
    try:
        # First, try to get draft information from ESPN API
        league.refresh_draft()
        
        # Check if draft has already happened
        if hasattr(league, 'espn_request'):
            try:
                draft_data = league.espn_request.get_league_draft()
                draft_detail = draft_data.get('draftDetail', {})
                
                # If draft is completed, only send completion message once (today only)
                if draft_detail.get('drafted', False):
                    logger.info("Draft is completed according to ESPN API")
                    # Get the draft completion date if available
                    try:
                        # Try to get the draft date from the API
                        draft_timestamp = draft_detail.get('date')
                        logger.info(f"Draft timestamp from API: {draft_timestamp}")
                        if draft_timestamp:
                            draft_completion_date = datetime.fromtimestamp(draft_timestamp / 1000).date()
                            today = date.today()
                            logger.info(f"Draft completion date: {draft_completion_date}, Today: {today}")
                            
                            # Send completion message only the day after draft completion
                            days_since_draft = (today - draft_completion_date).days
                            logger.info(f"Days since draft completion: {days_since_draft}")
                            
                            if days_since_draft > 1:
                                logger.info("More than 1 day since draft - returning empty string")
                                return ""  # Don't send any message more than 1 day after draft completion
                            elif days_since_draft == 1:
                                logger.info("Draft was completed yesterday - sending completion message")
                                # Continue to send completion message below
                            else:  # days_since_draft == 0 or < 0
                                logger.info("Draft completed today or in future - not sending completion message yet")
                                return ""
                        else:
                            logger.info("No draft timestamp available from API")
                    except (KeyError, ValueError, TypeError) as e:
                        logger.info(f"Error getting draft date: {e}")
                        # If we can't get the draft date, don't send repeated messages
                        # Check if this is likely the first day after draft (league.current_week == 1)
                        if league.current_week > 1:
                            logger.info(f"League current week > 1 ({league.current_week}) - returning empty string")
                            return ""
                    
                    if hasattr(league, 'draft') and league.draft:
                        total_picks = len(league.draft)
                        teams = league.settings.team_count if hasattr(league.settings, 'team_count') else len(set([pick.team for pick in league.draft]))
                        rounds = total_picks // teams if teams > 0 else 0
                        
                        return f"✅ DRAFT COMPLETED! ✅\n" \
                               f"Your {league.settings.name if hasattr(league.settings, 'name') else 'league'} " \
                               f"completed their {rounds}-round draft with {total_picks} total picks!\n" \
                               f"Good luck this season!"
                    else:
                        return "✅ DRAFT COMPLETED! ✅\nYour draft has been completed. Good luck this season!"
                
                # If draft is in progress
                elif draft_detail.get('inProgress', False):
                    return "🔴 DRAFT IN PROGRESS! 🔴\nYour draft is currently happening! Get in there!"
                
            except Exception as e:
                # ESPN API call failed, fall back to manual date if provided
                pass
        
    except Exception as e:
        # ESPN API completely failed, fall back to manual date if provided
        pass
    
    # No draft info available - check if we're in pre-season
    try:
        if league.current_week == 0:
            return "📋 DRAFT REMINDER 📋\n" \
                   "Your league is in pre-season! Draft hasn't been scheduled yet.\n" \
                   "Check your ESPN league settings to schedule your draft."
        else:
            return ""  # Don't send unknown status messages during the season
    except Exception:
        return ""  # If we can't determine anything, don't send a message


def completed_matchups(league):
    """
    Number of regular season matchups that have finished.

    Derived from team records rather than the week counters, because
    scoringPeriodId and current_week both drift at the season boundary while
    wins + losses + ties is always exactly what has been played.

    Parameters
    ----------
    league: object
        The league object to inspect.

    Returns
    -------
    int
        Matchups completed so far, 0 before the season starts.
    """

    if not league.teams:
        return 0
    return max(t.wins + t.losses + t.ties for t in league.teams)


def format_record(team, show_ties=False):
    """Format a team's record as W-L, or W-L-T when any team in the league has tied."""

    if show_ties:
        return '%d-%d-%d' % (team.wins, team.losses, team.ties)
    return '%d-%d' % (team.wins, team.losses)


def playoff_status(team, teams, playoff_spots, weeks_remaining):
    """
    Whether a team has clinched a playoff berth or been eliminated.

    Both tests are deliberately conservative: a rival that can merely *match*
    the team's win total is treated as able to pass it, since seeding ties are
    broken on points and are not predictable from records alone. A team is only
    reported as clinched when no combination of remaining results can miss it.

    Parameters
    ----------
    team: object
        The team to classify.
    teams: list
        Every team in the league.
    playoff_spots: int
        Number of playoff berths available.
    weeks_remaining: int
        Regular season matchups still to be played.

    Returns
    -------
    str
        'x' if clinched, 'e' if eliminated, '' if still undecided.
    """

    rivals = [t for t in teams if t is not team]

    could_catch = sum(1 for t in rivals if t.wins + weeks_remaining >= team.wins)
    if could_catch < playoff_spots:
        return 'x'

    max_wins = team.wins + weeks_remaining
    if sum(1 for t in rivals if t.wins > max_wins) >= playoff_spots:
        return 'e'

    return ''


def wins_to_clinch(team, teams, playoff_spots, weeks_remaining):
    """
    Fewest additional wins that guarantee a team a playoff spot.

    Returns 0 if already clinched, or None if no number of wins can guarantee
    it (the team can still be passed even by winning out).
    """

    for extra in range(0, weeks_remaining + 1):
        final_wins = team.wins + extra
        contenders = sum(1 for t in teams
                         if t is not team and t.wins + weeks_remaining >= final_wins)
        if contenders < playoff_spots:
            return extra
    return None


def get_playoff_picture(league, week=None):
    """
    Current playoff seeding, who is in, who is out, and what it takes to clinch.

    Seeding comes from league.standings(), which is ESPN's own ordering with the
    league's tiebreakers already applied.

    Parameters
    ----------
    league: object
        The league object for which the playoff picture is generated.
    week: int, optional
        Unused; accepted so this matches the signature of the other report
        functions and can be scheduled the same way.

    Returns
    -------
    str
        The playoff picture, or an empty string before any games are played.
    """

    teams = league.teams
    playoff_spots = getattr(league.settings, 'playoff_team_count', 0) or 0
    reg_season_count = getattr(league.settings, 'reg_season_count', 0) or 0
    if not teams or playoff_spots <= 0 or reg_season_count <= 0:
        return ''

    played = completed_matchups(league)
    if played == 0:
        # Nothing to show before week 1 is in the books.
        return ''

    weeks_remaining = max(reg_season_count - played, 0)
    show_ties = any(t.ties for t in teams)

    if weeks_remaining:
        subtitle = '%d played, %d to go - top %d make the playoffs' % (
            played, weeks_remaining, playoff_spots)
    else:
        subtitle = 'Regular season complete - top %d make the playoffs' % playoff_spots

    text = ['Playoff Picture', subtitle, '']

    clinched = eliminated = False
    for seed, team in enumerate(league.standings(), start=1):
        status = playoff_status(team, teams, playoff_spots, weeks_remaining)
        clinched = clinched or status == 'x'
        eliminated = eliminated or status == 'e'
        text.append('%2d: %-4s %-7s %1s %5.1f%%' % (
            seed, team.team_abbrev, '(' + format_record(team, show_ties) + ')',
            status, team.playoff_pct))
        if seed == playoff_spots:
            text.append('----------- cut line -----------')

    legend = []
    if clinched:
        legend.append('x = clinched')
    if eliminated:
        legend.append('e = eliminated')
    if legend:
        text += ['', ', '.join(legend)]

    if weeks_remaining:
        scenarios = []
        for team in league.standings():
            if playoff_status(team, teams, playoff_spots, weeks_remaining):
                continue
            need = wins_to_clinch(team, teams, playoff_spots, weeks_remaining)
            if need:
                scenarios.append('%s clinches with %d more win%s' % (
                    team.team_abbrev, need, '' if need == 1 else 's'))
        if scenarios:
            text += [''] + scenarios[:6]

    return '\n'.join(text)


def drafted_player_points(league, picks, chunk_size=50):
    """
    Season points for every drafted player, keyed by player id.

    player_info accepts a list, so this costs one request per chunk_size picks
    rather than one per pick. Players ESPN no longer returns (retired, or never
    rostered) are simply absent and treated as zero by the caller.
    """

    points = {}
    ids = [p.playerId for p in picks if p.playerId]

    for start in range(0, len(ids), chunk_size):
        try:
            info = league.player_info(playerId=ids[start:start + chunk_size])
        except Exception:
            # One bad chunk should not sink the whole report.
            continue
        if info is None:
            continue
        if not isinstance(info, list):
            info = [info]
        for player in info:
            points[player.playerId] = player.total_points or 0

    return points


DRAFT_GRADES = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']


def get_draft_report(league, min_weeks=4, list_size=5):
    """
    Grade every team's draft, and name the biggest steals and busts.

    A pick's value is how far its player's scoring rank beat the slot it was
    taken at: a player taken 100th who finished 10th in scoring among drafted
    players is +90. Team grades rank teams by their average pick value, so they
    are relative to this league rather than an absolute scale.

    Parameters
    ----------
    league: object
        The league object whose draft is graded.
    min_weeks: int, optional
        Matchups that must be complete before grades mean anything, default 4.
    list_size: int, optional
        How many steals and busts to list, default 5.

    Returns
    -------
    str
        The draft report, or an empty string if the league has no draft data.
    """

    picks = getattr(league, 'draft', None)
    if not picks:
        return ''

    played = completed_matchups(league)
    if played < min_weeks:
        return ('Draft report card needs a few weeks of scoring to mean anything. '
                'Check back after week %d.' % min_weeks)

    points = drafted_player_points(league, picks)
    if not points:
        return ''

    ordered = list(enumerate(picks, start=1))
    by_points = sorted(ordered, key=lambda op: points.get(op[1].playerId, 0), reverse=True)

    # value > 0 means the player outscored the slot he was taken at.
    value = {}
    for scoring_rank, (overall, _) in enumerate(by_points, start=1):
        value[overall] = overall - scoring_rank

    team_values = {}
    for overall, pick in ordered:
        team_values.setdefault(pick.team, []).append(value[overall])

    ranked_teams = sorted(((sum(v) / len(v), t) for t, v in team_values.items()),
                          key=lambda av: av[0], reverse=True)

    text = ['Draft Report Card',
            'Value = where a pick finished in scoring vs. where it was taken.', '',
            'Team Grades']
    for index, (avg, team) in enumerate(ranked_teams):
        grade = DRAFT_GRADES[min(index * len(DRAFT_GRADES) // len(ranked_teams),
                                 len(DRAFT_GRADES) - 1)]
        text.append('%2d: %-4s %-2s %+6.1f' % (
            index + 1, getattr(team, 'team_abbrev', '?'), grade, avg))

    def describe(overall, pick):
        return '  R%s.%s %-22s %-4s %6.1f pts (%+d)' % (
            pick.round_num, pick.round_pick, pick.playerName[:22],
            getattr(pick.team, 'team_abbrev', '?'),
            points.get(pick.playerId, 0), value[overall])

    by_value = sorted(ordered, key=lambda op: value[op[0]], reverse=True)

    text += ['', 'Biggest Steals']
    for overall, pick in by_value[:list_size]:
        text.append(describe(overall, pick))

    text += ['', 'Biggest Busts']
    for overall, pick in list(reversed(by_value))[:list_size]:
        text.append(describe(overall, pick))

    return '\n'.join(text)
