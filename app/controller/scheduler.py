from typing import List

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings

database_uri = Settings().DATABASE_URI

jobstores = {
    'default': SQLAlchemyJobStore(url=database_uri)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 3,
    'misfire_grace_time': 3600
}

sch = AsyncIOScheduler(jobstores=jobstores, job_defaults=job_defaults, timezone=utc)
sch.start()


def get_scheduler():
    return sch


def add_schedule_from_scheduler(func, args: List, cron_expression: str):
    job = sch.add_job(func, CronTrigger.from_crontab(cron_expression), args, jitter=5,
                      max_instances=1)
    return job


def edit_schedule_from_scheduler(args: List, cron_expression: str, job_id: str):
    job = sch.get_job(job_id)
    print(job)
    print(job_id)
    if job:
        new_job: Job = sch.modify_job(job_id, args=args, trigger=CronTrigger.from_crontab(cron_expression))
        return sch.reschedule_job(new_job.id, trigger=CronTrigger.from_crontab(cron_expression))
    else:
        return None


def remove_schedule_from_scheduler(job_id: str):
    job = sch.get_job(job_id)
    if job:
        sch.remove_job(job_id=job_id)


def get_jobs() -> List[Job]:
    return sch.get_jobs()
