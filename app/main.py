import logging
from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from sqlmodel import Session, SQLModel, select
from .database import engine, get_db
from .models import Pipelines, PipelineCreate, Jobs, JobCreate
from uuid import UUID
from .services.etl import run_pipeline
from .logs import setup_logging

setup_logging()
logger = logging.getLogger("pipeline")

logger.info("Initializing API and Database schemas...")
try:
    SQLModel.metadata.create_all(engine)
    logger.info("Database schemas verified/created successfully.")
except Exception:
    logger.exception("FATAL: Failed to initialize database schemas on startup")
    raise

app = FastAPI()

@app.get("/")
def checkConnection(db: Session = Depends(get_db)):
    try:
        # DEBUG: Good for high-frequency health checks
        logger.debug("Healthcheck: Probing database connection")
        db.exec(select(1))
        return {"status": "Connected to Database!"}
    except Exception as e:
        logger.exception("Healthcheck failed: Database unreachable")
        return {"error": "Service Unavailable"}, 503

@app.post("/pipelines", response_model=Pipelines)
async def createPipelines(pipeline_data: PipelineCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new pipeline: {pipeline_data.name}")
    
    try:
        db_pipeline = Pipelines.model_validate(pipeline_data)
        db.add(db_pipeline)
        db.commit()
        db.refresh(db_pipeline)
        
        logger.info(f"Pipeline created successfully with ID: {db_pipeline.id}")
        return db_pipeline
    except Exception:
        logger.exception("Failed to create pipeline in database")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/pipelines")
async def getPipelines(db: Session = Depends(get_db), offset: int=0, limit: int = Query(default=100, le=100),):
    try:
        pipelines = db.exec(select(Pipelines).offset(offset).limit(limit)).all()
        logger.info("Succesfully Retrieved Pipelines")
    except Exception:
        logger.exception("Failed to retrieve pipelines")
        return {"error": "Service Unavailable"}, 503
    return pipelines

@app.get("/pipelines/{pipe_id}")
async def getPipeline(pipe_id: UUID, db: Session= Depends(get_db)):
    try:
        pipelines = db.exec(select(Pipelines).where(Pipelines.id == pipe_id)).all()
        logger.info("Succesfully Retrieved Pipeline")
    except Exception:
        logger.exception("Failed to retrieve pipeline")
        return {"error": "Service Unavailable"}, 503

    return pipelines

@app.delete("/pipelines/{pipe_id}")
async def deletePipeline(pipe_id: UUID, db: Session = Depends(get_db)):
    pipeline = db.get(Pipelines, pipe_id)
    if not pipeline:
        logger.warning(f"Delete failed: Pipeline {pipe_id} not found")
        raise HTTPException(status_code=404, detail="Pipeline not Found")
    
    db.delete(pipeline)
    db.commit()
    logger.info(f"Pipeline {pipe_id} deleted successfully")
    return {"ok": True}

@app.post("/pipelines/{pipe_id}/run")
async def createJob(pipe_id: UUID, job_data: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    pipeline = db.get(Pipelines, pipe_id)

    if not pipeline:
        logger.warning(f"Run failed: Pipeline {pipe_id} not found")
        raise HTTPException(status_code=404, detail="Pipeline not Found")

    db_job = Jobs.model_validate(job_data, update={"pipeline_id": pipe_id})
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    logger.info(f"Job {db_job.id} queued for Pipeline {pipe_id}")
    
    background_tasks.add_task(run_pipeline, pipe_id, db_job.id, db)
    return db_job

@app.get("/pipelines/{pipe_id}/jobs")
async def getJobs(pipe_id: UUID, db: Session= Depends(get_db)):
    try:
        jobs = db.exec(select(Jobs).where(Jobs.pipeline_id==pipe_id)).all()
        logger.info("Succesfully Retrieved Pipeline")
    except Exception:
        logger.exception("Failed to retrieve pipeline")
        return {"error": "Service Unavailable"}, 503

    return jobs

@app.get("/jobs/{job_id}")
async def jobStatus(job_id: UUID, db: Session = Depends(get_db)):
    try:
        job = db.exec(select(Jobs).where(Jobs.id==job_id)).all()
        logger.info("Succesfully Retrieved Pipeline")
    except Exception:
        logger.exception("Failed to retrieve pipeline")
        return {"error": "Service Unavailable"}, 503
    return job
