from apscheduler.schedulers.blocking import BlockingScheduler
from gamedaybot.espn.espn_bot import espn_bot
from gamedaybot.espn.env_vars import get_env_vars


def scheduler():
    """
    This function is used to schedule jobs to send messages.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    data = get_env_vars()
    game_timezone = 'America/New_York'
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15 * 60})
    ff_start_date = data['ff_start_date']
    ff_end_date = data['ff_end_date']
    my_timezone = data['my_timezone']

    # close scores (within 15.99 points): monday evening at 6:30pm east coast time.
    # power rankings:                     tuesday evening at 6:30pm local time.
    # trophies:                           tuesday morning at 7:30am local time.
    # standings:                          wednesday morning at 7:30am local time.
    # waiver report:                      wednesday morning at 7:31am local time. (optional)
    # matchups:                           thursday evening at 7:30pm east coast time.
    # score update:                       friday, monday, and tuesday morning at 7:30am local time.
    # player monitor report:              sunday morning at 7:30am local time.
    # score update:                       sunday at 4pm, 8pm east coast time.

    sched.add_job(espn_bot, 'cron', ['get_close_scores'], id='close_scores',
                  day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_power_rankings'], id='power_rankings',
                  day_of_week='tue', hour=20, minute=5, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_final'], id='final',
                  day_of_week='tue', hour=20, minute=40, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_standings'], id='standings',
                  day_of_week='wed', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_waiver_report'], id='waiver_report',
                  day_of_week='wed', hour=7, minute=31, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)

    if data['daily_waiver']:
        sched.add_job(
            espn_bot, 'cron', ['get_waiver_report'],
            id='waiver_report', day_of_week='mon, tue, thu, fri, sat, sun', hour=7, minute=31, start_date=ff_start_date,
            end_date=ff_end_date, timezone=my_timezone, replace_existing=True)

    sched.add_job(espn_bot, 'cron', ['get_matchups'], id='matchups',
                  day_of_week='thu', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_scoreboard_short'], id='scoreboard1',
                  day_of_week='fri,mon', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)

    if data['monitor_report']:
        sched.add_job(espn_bot, 'cron', ['get_monitor'], id='monitor',
                      day_of_week='thu, sun, mon', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                      timezone=my_timezone, replace_existing=True)

    sched.add_job(espn_bot, 'cron', ['get_scoreboard_short'], id='scoreboard2',
                  day_of_week='sun', hour='16,20', start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
     
    # sched.add_job(espn_bot, 'cron', ['get_cmc_still_injured'], id='cmc',
    #               day_of_week='mon, tue, wed, thu, fri, sat, sun', hour=7, minute=31, start_date=ff_start_date, 
    #               end_date=ff_end_date, timezone=my_timezone, replace_existing=True)
    

    # Draft reminder: daily at 9:00am local time, only if DRAFT_DATE is configured
    # End the reminders after the draft date + 2 days to prevent infinite running
    if data.get('draft_date'):
        from datetime import datetime, timedelta
        try:
            draft_date = datetime.strptime(data['draft_date'], '%Y-%m-%d').date()
            # Stop draft reminders 2 days after the draft date
            draft_end_date = draft_date + timedelta(days=2)
            sched.add_job(espn_bot, 'cron', ['get_draft_reminder'], id='draft_reminder',
                          hour=9, minute=0, timezone=my_timezone,
                          end_date=draft_end_date, replace_existing=True)
        except (ValueError, TypeError) as e:
            print(f"Invalid draft date format '{data['draft_date']}': {e}")

    print("Ready!")
    sched.start()
