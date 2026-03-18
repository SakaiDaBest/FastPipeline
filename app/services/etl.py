from sqlmodel import Session
from ..models import Jobs, Pipelines
from ..database import engine
from uuid import UUID
from datetime import datetime
from .extract.extract import read_csv
from .transform.customers import cleanCustomers
from .transform.orders import cleanOrders
from .transform.products import cleanProducts
from .transform.weather import cleanWeather
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger("pipeline")

class NotFoundError(Exception):
    pass

class PipelineError(Exception):
    pass

def run_pipeline(pipe_id: UUID, job_id: UUID, db: Session): 
    pipeline = db.get(Pipelines, pipe_id)
    if not pipeline:
        logger.error(f"Pipeline {pipe_id} not found")
        return

    job = db.get(Jobs, job_id)
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    job.status = "running"
    job.started_at = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    db.add(job)
    db.commit()
    logger.info(f"Job {job.id} started")

    try:
        match pipeline.source_type.upper():
            case "CSV":
                try:
                    df = read_csv(pipeline.source_config["path"])
                except Exception:
                    raise PipelineError(f"Source path {pipeline.source_config['path']} cannot be found or is not a CSV")

                if pipeline.name.lower() == "orders":
                    df = cleanOrders(df)
                elif pipeline.name.lower() == "customers":
                    df = cleanCustomers(df)
                elif pipeline.name.lower() == "products":
                    df = cleanProducts(df)
                else:
                    raise PipelineError(f"Pipeline name '{pipeline.name}' is not supported")

                if pipeline.destination_type.lower() == "postgres":
                    db_name = pipeline.destination_config.get("table") or f"{pipeline.name}-{job_id}"
                    logger.info(f"Saving to Database table: {db_name}")
                    df.to_sql(db_name, con=engine, if_exists='replace', index=False)
                elif pipeline.destination_type.lower() == "csv":
                    logger.info("Saving to CSV")
                    df.to_csv(f"./data/transformed/{pipeline.name}-{job.id}.csv", index=False)
                else:
                    raise PipelineError(f"Destination type '{pipeline.destination_type}' is not supported")

            case "API":
                if pipeline.name.lower() == "weather":
                    url = pipeline.source_config["url"]
                    params = pipeline.source_config.get("params", {})  # Fix was here
                    df = cleanWeather(url, params)
                else:
                    raise PipelineError(f"Pipeline name '{pipeline.name}' is not supported")

                if pipeline.destination_type.lower() == "postgres":
                    db_name = pipeline.destination_config.get("table") or f"{pipeline.name}-{job_id}"
                    logger.info(f"Saving to Database table: {db_name}")
                    df.to_sql(db_name, con=engine, if_exists='replace', index=False)
                elif pipeline.destination_type.lower() == "csv":
                    logger.info("Saving to CSV")
                    df.to_csv(f"./data/transformed/{pipeline.name}-{job.id}.csv", index=False)
                else:
                    raise PipelineError(f"Destination type '{pipeline.destination_type}' is not supported")

            case _:
                raise PipelineError(f"Source type '{pipeline.source_type}' is not supported")

        job.status = "success"
        job.records_processed = len(df)
        logger.info(f"Job {job.id} completed successfully, {len(df)} records processed")

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        logger.exception(f"Job {job.id} failed")

    finally:
        job.finished_at = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
        db.add(job)
        db.commit()
        db.refresh(job)

