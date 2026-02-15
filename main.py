from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
app = FastAPI()

class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

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
