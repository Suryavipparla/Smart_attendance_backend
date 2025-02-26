from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Faculty, Attendance
from datetime import datetime
import os
import cv2
import torch
import numpy as np
from tempfile import NamedTemporaryFile
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn
from utils.face_recognition import verify_faces  # Ensure this is correctly imported

router = APIRouter()

# -------------------------------
# 1. Load Anti-Spoofing Model
# -------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = nn.Linear(model.last_channel, 2)
model.load_state_dict(torch.load("best_antispoof_model.pth", map_location=device))
model.to(device)
model.eval()

# -------------------------------
# 2. Define Image Transform for Anti-Spoofing
# -------------------------------
test_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# -------------------------------
# 3. Anti-Spoofing Check Function
# -------------------------------
def predict_spoof(image_path: str) -> bool:
    """Returns True if image is real, False if spoofed"""
    img = cv2.imread(image_path)
    if img is None:
        return False  # Invalid image

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_tensor = test_transform(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)

    return predicted.item() == 1  # 1 => Real, 0 => Spoofed

# -------------------------------
# 4. Attendance API Endpoint
# -------------------------------
@router.post("/mark-attendance/")
async def mark_attendance(faculty_id: str = Form(...), image: UploadFile = UploadFile(...), db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    # Save uploaded image as temp file
    with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_uploaded:
        uploaded_path = temp_uploaded.name
        temp_uploaded.write(await image.read())

    # Save stored image as temp file
    with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_stored:
        stored_path = temp_stored.name
        temp_stored.write(faculty.image)

    # Step 1: **Anti-Spoofing Check**
    if not predict_spoof(uploaded_path):
        os.remove(uploaded_path)
        os.remove(stored_path)
        raise HTTPException(status_code=400, detail="Spoofed image detected! Access denied.")

    # Step 2: **Face Verification Check**
    if not verify_faces(uploaded_path, stored_path):
        os.remove(uploaded_path)
        os.remove(stored_path)
        raise HTTPException(status_code=401, detail="Face verification failed")

    # Remove temp files
    os.remove(uploaded_path)
    os.remove(stored_path)

    # Step 3: **Mark Attendance**
    current_time = datetime.now()
    today_date = current_time.date()
    
    attendance_record = (
        db.query(Attendance)
        .filter(Attendance.faculty_id == faculty_id)
        .filter(Attendance.date == today_date)
        .first()
    )
    
    if attendance_record:
        attendance_record.logout_time = current_time
        attendance_record.status = "present"
    else:
        attendance_record = Attendance(
            faculty_id=faculty_id,
            status="Present",
            login_time=current_time,
            logout_time=None,
            date=today_date,
        )
        db.add(attendance_record)
    
    db.commit()
    db.refresh(attendance_record)

    return {"message": "Attendance marked", "faculty_id": faculty_id, "status": "Present", "date": str(today_date)}
