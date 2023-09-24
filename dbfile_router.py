from fastapi import FastAPI, HTTPException,status, Depends, File, UploadFile,Query
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
from fastapi import APIRouter

router = APIRouter(
    prefix = '/DBOps',
    tags = ['Data Loading']
)
 
models.Base.metadata.create_all(bind=engine)
def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency= Annotated[Session, Depends(get_db)]

#@router.get("/sql/statements")
def issue_sql(db: db_dependency,sql: Annotated[str , Query(min_length=15)] ):
# write the SQL query inside the text() block
    with engine.connect() as conn:
        user='test'
        pwd='test123'
        json_ = json.dumps({'x': user})
        sql = text( 'CREATE USER '+ user + ' WITH PASSWORD :p ')
        result = conn.execute(sql,{'p':pwd })
        conn.commit()
        with engine.connect() as conn:
            stmt= text("select * from pg_catalog.pg_user where usename = :u")
            
            for row in conn.execute(stmt, {'u':user}):
                 print(f"{row.usename}")

    return {"status": "User added to Database", "User": user }

#with engine.connect() as conn, conn.begin():
#    stmt = text("INSERT INTO users (id, name) VALUES(:id, :name)")
#    conn.execute(stmt, [dict(id=1, name="test"), dict(id=2, name="testagain")])

def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=',', skiprows=1, converters={0: lambda s: str(s)})
    return data.tolist()

@router.post("/upload_csv_database/")
async def upload_data( db: db_dependency, file: UploadFile, seperator:str):
        # Get the file size (in bytes)
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # move the cursor back to the beginning
    await file.seek(0)

    if file_size > 2 * 1024 * 1024:
        # more than 2 MB
        raise HTTPException(status_code=200, detail="File too large")

    # check the content type (MIME type)
    content_type = file.content_type
    if content_type in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file )
    else:
        df = pd.read_excel(file.file )

   
    try:

        tablename  =get_file_name(file.filename)

        print(tablename)
        print(seperator)
        df.to_sql(tablename , engine, if_exists= 'replace', index= False)
        return {"status": status.HTTP_200_OK, "detail":f"{file.filename} - upload to postgres successfully"}

    except:
        print("Sorry, some error has occurred!")

    finally:
        engine.dispose()
def get_file_name(file_path):
        file_path_components = file_path.split('/')
        file_path_components = file_path.split('\\')

        file_name_and_extension = file_path_components[-1].rsplit('.', 1)
        return file_name_and_extension[0]
# import os
# path = 'your path'
# all_csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
# for f in all_csv_files:
#     data = pd.read_csv(os.path.join(path, f), sep="|", names=col)

# # list without .csv
# files = [f[:-4] for f all_csv_files]

