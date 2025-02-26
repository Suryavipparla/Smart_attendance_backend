from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
import aiofiles
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import Faculty

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/register/")
async def submit_data(
    faculty_id: str = Form(...),
    name: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await image.read()
    faculty = Faculty(faculty_id=faculty_id, name=name, image=content)
    db.add(faculty)
    db.commit()
    return JSONResponse(content={"message": "Faculty registered successfully"}, status_code=200)

@router.post("/update-image/")
async def update_image(
    faculty_id: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    update = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not update:
        raise HTTPException(status_code=404, detail=f"No faculty found with ID: {faculty_id}")

    if not update.image:
        raise HTTPException(status_code=400, detail=f"No image found for faculty ID: {faculty_id}")

    async with aiofiles.open(f"{UPLOAD_DIR}/{image.filename}", "wb") as out_file:
        content = await image.read()
        await out_file.write(content)

    update.image = content
    db.commit()
    return JSONResponse(content={"message": "Image updated successfully"}, status_code=200)

@router.get("/get-image/")
async def get_image(faculty_id: str):
    db = SessionLocal()
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail=f"No faculty found with ID: {faculty_id}")

    if not faculty.image:
        raise HTTPException(status_code=400, detail=f"No image found for faculty ID: {faculty_id}")

    return Response(content=faculty.image, media_type="image/jpeg")
