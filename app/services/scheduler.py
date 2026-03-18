from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from ..models import Pipelines, Jobs
from ..database import engine
from .etl import run_pipeline
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger("scheduler")

scheduler = AsyncIOScheduler(timezone="Asia/Kuala_Lumpur")

def execute_pipeline(pipe_id):
    with Session(engine) as db:
        job = Jobs(
            id=uuid4(),
            pipeline_id=pipe_id,
            status="pending",
            started_at=datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        run_pipeline(pipe_id, job.id, db)
        logger.info(f"Scheduled job completed for pipeline {pipe_id}")

def load_scheduled_pipelines():
    """Load all pipelines with a cron_expression and schedule them."""
    with Session(engine) as db:
        pipelines = db.exec(select(Pipelines).where(Pipelines.cron_expression != None)).all()
        for pipeline in pipelines:
            schedule_pipeline(pipeline)
        logger.info(f"Loaded {len(pipelines)} scheduled pipelines")

def schedule_pipeline(pipeline: Pipelines):
    """Add or replace a pipeline job in the scheduler."""
    job_id = f"pipeline_{pipeline.id}"
    # Remove existing job if it exists
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    if pipeline.cron_expression:
        trigger = CronTrigger.from_crontab(pipeline.cron_expression, timezone="Asia/Kuala_Lumpur")
        scheduler.add_job(
            execute_pipeline,
            trigger=trigger,
            args=[pipeline.id],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled pipeline '{pipeline.name}' with cron: {pipeline.cron_expression}")

def unschedule_pipeline(pipe_id):
    """Remove a pipeline job from the scheduler."""
    job_id = f"pipeline_{pipe_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Unscheduled pipeline {pipe_id}")
