from sqlmodel import Field, Session, SQLModel, create_engine, select
from ..models import Jobs, Pipelines
from ..database import get_db, engine
from uuid import UUID
from datetime import datetime
from .extract.extract import read_csv
from .transform.customers import cleanCustomers
from .transform.orders import cleanOrders
from .transform.products import cleanProducts
import numpy as np
from fastapi import Depends
import pandas as pd

async def run_pipeline(pipe_id: UUID, job_id: UUID, db: Session): 

    pipeline = db.get(Pipelines, pipe_id)
    if not pipeline:
        print("Pipeline not found")
        return

    job = db.get(Jobs, job_id)
    if not job:
        print("Job not found")
        return

    job.status = "running"
    job.started_at = datetime.utcnow() 
    db.add(job)
    db.commit()

    try:
        match pipeline.source_type:
            case "CSV":
                df = read_csv(pipeline.source_path)
                
                if pipeline.name == "orders":
                    df = cleanOrders(df)
                elif pipeline.name == "customers":
                    df = cleanCustomers(df)
                elif pipeline.name == "products":
                    df = cleanProducts(df)
                
                if pipeline.destination_type == "postgres":
                    df.to_sql(pipeline.name, con=engine, if_exists='replace', index=False)
                elif pipeline.destination_type == "CSV":
                    df.to_csv(f"./data/transformed/{pipeline.name}.csv", index=False)

                job.status = "success"
                job.records_processed = len(df) 
                
            case _:
                job.status = "failed"
                job.error_message = "Source Type Not Supported"
    
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)

    job.finished_at = datetime.utcnow()
    db.add(job)
    db.commit()
    db.refresh(job)

    
