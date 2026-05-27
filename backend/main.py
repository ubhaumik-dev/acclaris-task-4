from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil
import os

app =  FastAPI()

#CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#DATABASE

DATABASE_URL = "sqlite:///./files.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
#upload 

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

#database table

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    fileName = Column(String)
    filePath = Column(String)

Base.metadata.create_all(bind=engine)

#uploading file api

@app.post("/upload-file")
def upload_file(file:UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()

    new_file = UploadedFile(
        fileName = file.filename,
        filePath = file_location
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    db.close()

    return {
        "message" : "File upload successful",
        "file" : {
            "id": new_file.id,
            "filename": new_file.fileName
        }
    }

#get files
@app.get("/get-files")
def get_files():
    db = SessionLocal()
    files = db.query(UploadedFile).all()

    db.close()

    result = []

    for file in files:
        result.append({
            "id" : file.id,
            "filename": file.fileName,
            "filepath": file.filePath
        })

    return result

#download files 

@app.get("/download-file/{file_id}")
def download_file(file_id : int):
    db = SessionLocal()

    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    db.close()
    if not file:
        return {"error" : "file not found"}
    
    return FileResponse(
        path = file.filePath,
        filename = file.fileName,
        media_type = "application/octet-stream"
    )

#delete file

@app.delete("/delete-file/{file_id}")
def delete_file(file_id: int):
    db = SessionLocal()

    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    if not file:
        db.close()
        return{"error" : "file not found"}

    if os.path.exists(file.filePath):
        os.remove(file.filePath)

    db.delete(file)
    db.commit()
    db.close()
    return{
        "message" : "file deleted successfully"
    }


#view file
@app.get("/view-file/{file_id}")
def view_file(file_id: int):
    db= SessionLocal()

    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    db.close()

    if not file:
        return {"error" : "file not found"}

    return FileResponse(file.filePath)