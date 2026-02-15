from fastapi import FastAPI, Depends
import psycopg2
import os
from sqlmodel import SQLModel,Session, select
from database import engine, get_db
import models

SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.get("/")
def checkConnection(db: Session = Depends(get_db)):
    try:
        db.exec(select(1)) 
        return {"status": "Connected to Database via SQLModel!"}
    except Exception as e:
        return {"error": str(e)}
@app.post("/pipelines")
async def showPipelines(db: Session= Depends(get_db)):
    pass


@app.get("/pipelines")
async def getPipelines(db: Session = Depends(get_db)):
    pass


@app.get("/pipelines/{id}")
async def getPipeline(user_id: int, db: Session= Depends(get_db)):
    pass


@app.delete("/pipelines/{id}")
async def deletePipeline(user_id: int, db: Session= Depends(get_db)):
    pass
