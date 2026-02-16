from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime

class PipelineBase(SQLModel):
    # id: UUID = Field(default_factory=uuid4, primary_key = True)
    name: str = Field(max_length=255)
    source_type: str = Field(max_length=50)
    source_path: str 
    destination_type: str = Field(max_length=50)
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # jobs : List["Jobs"] = Relationship(back_populates="pipeline", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class PipelineCreate(PipelineBase):
    pass

class Pipelines(PipelineBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    jobs : List["Jobs"] = Relationship(back_populates="pipeline", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class JobBase(SQLModel):
    status: str = Field(default="pending", max_length=20)
    records_processed: int = Field(default=0)

class JobCreate(JobBase):
    pass # What the user sends

class Jobs(JobBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    started_at: Optional[datetime] = Field(default=None)
    finished_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

    pipeline_id: UUID = Field(foreign_key="pipelines.id")
    pipeline: Pipelines = Relationship(back_populates="jobs")




# from pydantic import BaseModel
# from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, CheckConstraint
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from datetime import datetime
# from typing import List, Optional
# from uuid import UUID, uuid4
# from database import  Base
#
# class Pipeline(BaseModel):
#     __tablename__ = "pipelines"
#
#     id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
#     name: Mapped[str] = mapped_column(String(255))
#     source_type: Mapped[str] = mapped_column(String(50))
#     source_path: Mapped[str] = mapped_column(Text)
#     destination_type: Mapped[str] = mapped_column(String(50))
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#
#     jobs: Mapped[List["Job"]] = relationship(back_populates="pipeline", cascade="all, delete-orphan")
#
# class Job(Base):
#     __tablename__ = "jobs"
#
#     id: Mapped[UUID] = mapped_column(primary_key=True, defualt=uuid4)
#     pipeline_id: Mapped[UUID] = mapped_column(ForeignKey("pipelines.id"))
#     status: Mapped[str] = mapped_column(String(20), default="pending")
#     started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable = True)
#     finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable = True)
#     records_processed: Mapped[int] = mapped_column(Integer, default=0)
#     error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
#
#     pipeline: Mapped["Pipeline"] = relationship(back_populates="jobs")
#
#     __table_args__ = (
#         CheckConstraint(status.in_(["pending", "running", "success", "failed"]), name="check_status"),
#    )
