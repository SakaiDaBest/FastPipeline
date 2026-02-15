from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
import psycopg2
import os

app = FastAPI()

class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

@app.get("/")
def read_db():
    try:
        # Connect using the service name 'my-db' defined in docker-compose
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
async def showPipelines():
    pass


@app.get("/pipelines")
async def getPipelines():
    pass


@app.get("/pipelines/{id}")
async def getPipeline(id):
    pass


@app.delete("/pipelines/{id}")
async def deletePipeline(id):
    pass
