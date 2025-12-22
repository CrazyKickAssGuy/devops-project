from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://userman1:pass123123@db:5432/items_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

app = FastAPI()

def wait_for_db():
    retries = 10
    while retries > 0:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Successfully connected to the database!")
            return
        except Exception as e:
            print(f"Database not ready yet... ({retries} retries left). Error: {e}")
            retries -= 1
            time.sleep(3)
    raise Exception("Could not connect to the database after several retries.")

@app.on_event("startup")
def startup_event():
    wait_for_db()
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}
