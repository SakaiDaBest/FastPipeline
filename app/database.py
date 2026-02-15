from sqlmodel import create_engine, Session
import os

# Get your Docker env variables
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@my-db:5432/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DB_URL, echo=True)

def get_db():
    with Session(engine) as session:
        yield session
