from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import psycopg2
import os
from database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def readDb(db: Session = Depends(get_db)):
    try:
        conn = psycopg2.connect(
            host="my-db", 
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        return {"status": "Connected to Database!"}
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
