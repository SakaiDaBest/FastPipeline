from typing import Sequence
from fastapi import FastAPI, Depends, Query, HTTPException
import psycopg2
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select
from .database import engine, get_db
from .models import Pipelines, Jobs
from uuid import UUID

SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.get("/")
def checkConnection(db: Session = Depends(get_db)):
    try:
        db.exec(select(1)) 
        return {"status": "Connected to Database!"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/pipelines")
async def createPipelines(pipeline: Pipelines, db: Session= Depends(get_db)) -> Pipelines:
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline

@app.get("/pipelines")
async def getPipelines(db: Session = Depends(get_db), offset: int=0, limit: int = Query(default=100, le=100),) -> Sequence[Pipelines]:
    pipelines = db.exec(select(Pipelines).offset(offset).limit(limit)).all()
    return pipelines

@app.get("/pipelines/{id}")
async def getPipeline(pipe_id: UUID, db: Session= Depends(get_db)):
    pipelines = db.exec(select(Pipelines).where(Pipelines.id == pipe_id)).all()
    return pipelines

@app.delete("/pipelines/{id}")
async def deletePipeline(pipe_id: UUID, db: Session= Depends(get_db)):
    pipeline = db.get(Pipelines, pipe_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not Found")
    db.delete(pipeline)
    db.commit()
    return {"ok": True}
