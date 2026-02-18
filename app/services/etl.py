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

async def run_pipeline(path_id: UUID,job_id:UUID, db: Session=Depends(get_db)):
    sPath=db.exec(select(Pipelines.source_path).where(Pipelines.id==path_id))
    sType=db.exec(select(Pipelines.source_type).where(Pipelines.id==path_id))
    dPath=db.exec(select(Pipelines.destination_type).where(Pipelines.id==path_id))
    pipeName=db.exec(select(Pipelines.name).where(Pipelines.id==path_id))


    job_started_at = db.exec(select(Jobs.started_at).where(Jobs.id==job_id)).one()
    job_started_at = datetime.utcnow
    db.add(job_started_at)
    db.commit()
    db.refresh(job_started_at)

    match sType:
        case "CSV":
            df = read_csv(sPath)
        case _:
            print("This Type is not Supported")
            return
            
    
    print("Transforming...")
    if pipeName == "orders":
        cleanOrders(df)
    elif pipeName == "customers":
        cleanCustomers(df)
    elif pipeName == "prodcuts":
        cleanProducts(df)
    
    print(f"Loading into {dPath}")
    if dPath == "postgres":
        df.to_sql(f'{pipeName}', con=engine, if_exists='replace', index=False)
    elif dPath == "CSV":
        df.to_csv("~/Documents/Projects/FastPipeline/data/transformed/", index=False)



    
