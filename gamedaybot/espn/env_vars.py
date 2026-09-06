import os
from datetime import date
import gamedaybot.espn.functionality as espn
import gamedaybot.utils.util as utils


def get_env_vars():
    data = {}
    # Default to the current season. Hardcoded years silently rot: a past
    # END_DATE puts every cron job's end_date behind us, so no job ever fires.
    current_year = date.today().year

    try:
        ff_start_date = os.environ["START_DATE"]
    except KeyError:
        ff_start_date = '%d-09-05' % current_year

    data['ff_start_date'] = ff_start_date

    try:
        ff_end_date = os.environ["END_DATE"]
    except KeyError:
        ff_end_date = '%d-12-31' % current_year

    data['ff_end_date'] = ff_end_date

    try:
        my_timezone = os.environ["TIMEZONE"]
    except KeyError:
        my_timezone = 'America/New_York'

    data['my_timezone'] = my_timezone

    try:
        daily_waiver = utils.str_to_bool(os.environ["DAILY_WAIVER"])
    except KeyError:
        daily_waiver = False

    data['daily_waiver'] = daily_waiver

    try:
        monitor_report = utils.str_to_bool(os.environ["MONITOR_REPORT"])
    except KeyError:
        monitor_report = True

    data['monitor_report'] = monitor_report

    # Per-platform message caps. Every message is sent to *all* configured
    # platforms, so the limit has to be the smallest of the ones in use --
    # assigning in sequence meant the last platform read simply won.
    GROUPME_LIMIT = 1000
    SLACK_LIMIT = 40000
    # Discord caps message content at 2000 characters, and the bot wraps every
    # message in a ``` code fence, which costs 6 more.
    DISCORD_LIMIT = 2000 - 6

    limits = []

    try:
        bot_id = os.environ["BOT_ID"]
        limits.append(GROUPME_LIMIT)
    except KeyError:
        bot_id = 1

    try:
        slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        limits.append(SLACK_LIMIT)
    except KeyError:
        slack_webhook_url = 1

    try:
        discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
        limits.append(DISCORD_LIMIT)
    except KeyError:
        discord_webhook_url = 1

    str_limit = min(limits) if limits else SLACK_LIMIT

    if (len(str(bot_id)) <= 1 and
        len(str(slack_webhook_url)) <= 1 and
            len(str(discord_webhook_url)) <= 1):
        # Ensure that there's info for at least one messaging platform,
        # use length of str in case of blank but non null env variable
        raise Exception("No messaging platform info provided. Be sure one of BOT_ID, SLACK_WEBHOOK_URL, or DISCORD_WEBHOOK_URL env variables are set")

    data['str_limit'] = str_limit
    data['bot_id'] = bot_id
    data['slack_webhook_url'] = slack_webhook_url
    data['discord_webhook_url'] = discord_webhook_url

    data['league_id'] = os.environ["LEAGUE_ID"]

    try:
        year = int(os.environ["LEAGUE_YEAR"])
    except KeyError:
        year = current_year

    data['year'] = year

    try:
        swid = os.environ["SWID"]
    except KeyError:
        swid = '{1}'

    if swid.find("{", 0) == -1:
        swid = "{" + swid
    if swid.find("}", -1) == -1:
        swid = swid + "}"

    data['swid'] = swid

    try:
        espn_s2 = os.environ["ESPN_S2"]
    except KeyError:
        espn_s2 = '1'

    data['espn_s2'] = espn_s2

    try:
        test = utils.str_to_bool(os.environ["TEST"])
    except KeyError:
        test = False

    data['test'] = test

    try:
        top_half_scoring = utils.str_to_bool(os.environ["TOP_HALF_SCORING"])
    except KeyError:
        top_half_scoring = False

    data['top_half_scoring'] = top_half_scoring

    try:
        random_phrase = utils.str_to_bool(os.environ["RANDOM_PHRASE"])
    except KeyError:
        random_phrase = False

    data['random_phrase'] = random_phrase

    try:
        waiver_report = utils.str_to_bool(os.environ["WAIVER_REPORT"])
    except KeyError:
        waiver_report = False

    data['waiver_report'] = waiver_report

    try:
        data['init_msg'] = os.environ["INIT_MSG"]
    except KeyError:
        # do nothing here, empty init message
        pass

    try:
        discord_token = os.environ["DISCORD_TOKEN"]
    except KeyError:
        discord_token = None

    data['discord_token'] = discord_token

    try:
        discord_server_id = os.environ["DISCORD_SERVER_ID"]
    except KeyError:
        discord_server_id = None

    data['discord_server_id'] = discord_server_id

    try:
        draft_date = os.environ["DRAFT_DATE"]
    except KeyError:
        draft_date = None

    data['draft_date'] = draft_date

    return data
