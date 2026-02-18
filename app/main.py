from typing import Sequence
from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from sqlmodel import Field, Session, SQLModel, create_engine, select
from .database import engine, get_db
from .models import Pipelines, PipelineCreate, Jobs, JobCreate
from uuid import UUID
from .services.etl import run_pipeline

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
async def createPipelines(pipeline_data: PipelineCreate, db: Session= Depends(get_db)) -> Pipelines:
    db_pipeline = Pipelines.model_validate(pipeline_data)
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline

@app.get("/pipelines")
async def getPipelines(db: Session = Depends(get_db), offset: int=0, limit: int = Query(default=100, le=100),) -> Sequence[Pipelines]:
    pipelines = db.exec(select(Pipelines).offset(offset).limit(limit)).all()
    return pipelines

@app.get("/pipelines/{pipe_id}")
async def getPipeline(pipe_id: UUID, db: Session= Depends(get_db)):
    pipelines = db.exec(select(Pipelines).where(Pipelines.id == pipe_id)).all()
    return pipelines

@app.delete("/pipelines/{pipe_id}")
async def deletePipeline(pipe_id: UUID, db: Session= Depends(get_db)):
    pipeline = db.get(Pipelines, pipe_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not Found")
    db.delete(pipeline)
    db.commit()
    return {"ok": True}

@app.post("/pipelines/{pipe_id}/run")
async def createJob(pipe_id: UUID, job_data: JobCreate, background_tasks: BackgroundTasks, db: Session= Depends(get_db)) -> Jobs:
    pipeline = db.get(Pipelines, pipe_id)

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not Found")

    db_job = Jobs.model_validate(job_data, update={"pipeline_id": pipe_id})
    job_id = db_job.id
    pipe_id = db_job.pipeline_id
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    background_tasks.add_task(run_pipeline, pipe_id,job_id,db)

    return db_job

@app.get("/pipelines/{pipe_id}/jobs")
async def getJobs(pipe_id: UUID, db: Session= Depends(get_db)):
    pipelines = db.exec(select(Jobs).where(Jobs.pipeline_id==pipe_id)).all()
    return pipelines

@app.get("/jobs/{job_id}")
async def jobStatus(job_id: UUID, db: Session = Depends(get_db)):
    job = db.exec(select(Jobs.status).where(Jobs.id==job_id)).all()
    return job
