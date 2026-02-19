from fastapi import HTTPException
from sqlmodel import Session
from ..models import Jobs, Pipelines
from ..database import engine
from uuid import UUID
from datetime import datetime
from .extract.extract import read_csv
from .transform.customers import cleanCustomers
from .transform.orders import cleanOrders
from .transform.products import cleanProducts
from zoneinfo import ZoneInfo
import logging

logger =logging.getLogger("pipeline")

class NotFoundError(Exception):
    pass

def run_pipeline(pipe_id: UUID, job_id: UUID, db: Session): 
    try:
        pipeline = db.get(Pipelines, pipe_id)
        if not pipeline:
            raise NotFoundError("Pipeline not found")

    except Exception:
        logger.exception("Pipeline not found")
        return {"error": "Pipeline cannot be found!"}, 404
        
    try:
        job = db.get(Jobs, job_id)
        if not job:
            raise NotFoundError("Job not found")
            
    except Exception:
        logger.exception("Job not found")
        return {"error": "Job cannot be found!"}, 404

    job.status = "running"
    job.started_at = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    try:
        db.add(job)
        db.commit()
        logger.info(f"Successfully changed status of Job {job.id} to {job.status}")
    except Exception:
        logger.exception(f"Failed to change status of Job {job.id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    try:
        match pipeline.source_type.upper():
            case "CSV":
                try:
                    logger.debug("Reading Source Path for CSV File")
                    df = read_csv(pipeline.source_path)
                except Exception:
                    logger.exception(f"{pipeline.source_path} cannot be found or File is not a CSV!")
                    raise HTTPException(status_code=404, detail=f"Source Path {pipeline.source_path} cannot be found or File is not a CSV!")
                logger.info("Source Path verified and read")
                
                logger.debug("Verifying Pipeline Name")
                try:
                    if pipeline.name.lower() == "orders":
                        logger.info("Pipeline Name has been Verified")
                        logger.info("Cleaning Now")
                        df = cleanOrders(df)
                        logger.info("Cleaning has Completed")
                    elif pipeline.name.lower() == "customers":
                        logger.info("Pipeline Name has been Verified")
                        logger.info("Cleaning Now")
                        df = cleanCustomers(df)
                        logger.info("Cleaning has Completed")
                    elif pipeline.name.lower() == "products":
                        logger.info("Pipeline Name has been Verified")
                        logger.info("Cleaning Now")
                        df = cleanProducts(df)
                        logger.info("Cleaning has Completed")
                    else: 
                        logger.error(f"Pipeline Name does not match with available options")
                        raise HTTPException(status_code=405, detail="Pipeline Not Accepted!")
                except Exception:
                    logger.exception(f"Internal Server Error")
                    raise HTTPException(status_code=500, detail="An Internal Error has Occured")

                logger.debug("Verifying Pipeline Destination")

                if pipeline.destination_type == "postgres":
                    db_name=pipeline.name+"-"+str(job_id)
                    logger.info("Saving to Database")
                    df.to_sql(db_name, con=engine, if_exists='replace', index=False)
                elif pipeline.destination_type == "CSV":
                    logger.info(f"Saving to CSV")
                    df.to_csv(f"./data/transformed/{pipeline.name}-{job.id}.csv", index=False)
                else:
                    logger.error(f"Pipeline Destination Path does not match with available options")
                    raise HTTPException(status_code=405, detail="Pipeline Destination Not Accepted!")
                
                logger.info("Job has Completed")

                job.status = "success"
                job.records_processed = len(df) 
                
            case _:
                job.status = "failed"
                job.error_message = "Source Type Not Supported"
                raise HTTPException(status_code=405, detail=f"Source Type is not Accepted")
    
    except Exception:
        job.status = "failed"
        logger.exception("Internal Server Error")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    job.finished_at = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    
    logger.info("Saving Job Details to Database...")
    try:
        db.add(job)
        db.commit()
        db.refresh(job)
    except Exception:
        logger.exception("Failed to create pipeline in database")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

    
