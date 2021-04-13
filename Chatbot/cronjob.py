from apscheduler.schedulers.background import BackgroundScheduler

from main import cronjob

scheduler = BackgroundScheduler()
scheduler.add_job(cronjob, "interval", seconds=7500)

scheduler.start()
