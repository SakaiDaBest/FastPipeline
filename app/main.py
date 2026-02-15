from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import psycopg2
import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

app = FastAPI()


class Base(DeclarativeBase):
    pass

class Pipeline(BaseModel):
    __tablename__ = "pipelines"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(50))
    source_path: Mapped[str] = mapped_column(Text)
    destination_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    jobs: Mapped[List["Job"]] = relationship(back_populates="pipeline", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(primary_key=True, defualt=uuid4)
    pipeline_id: Mapped[UUID] = mapped_column(ForeignKey("pipelines.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable = True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable = True)
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    pipeline: Mapped["Pipeline"] = relationship(back_populates="jobs")

    __table_args__ = (
        CheckConstraint(status.in_(["pending", "running", "success", "failed"]), name="check_status"),
    )


def connecton():
    try:
        # Connect using the service name 'my-db' defined in docker-compose
        conn = psycopg2.connect(
            host="my-db", 
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        return conn
    except Exception as e:
        return e


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
