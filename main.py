from fastapi import FastAPI, HTTPException,status, Depends, File, UploadFile
from typing import List, Annotated
from schema import AppRoleUser,Application,UserCreate,Role
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import result
import json
import pandas as pd
import time, datetime
from numpy import genfromtxt
from passlib.context import CryptContext
import db_router,dbfile_router
app = FastAPI()
app.include_router(db_router.router)
app.include_router(dbfile_router.router)

models.Base.metadata.create_all(bind=engine)
def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
async def home():
    return {"Home": "FastAPI SQL Alchemy and Postgresql"}
db_dependency= Annotated[Session, Depends(get_db)]

