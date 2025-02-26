from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models import Employee  # Ensure Employee model exists
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from database import get_db

router = APIRouter()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Admin adds an employee (unchanged)
@router.post("/api/add-employee/")
def add_employee(employee_id: str = Form(...), name: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Check if employee already exists
    existing_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Hash the password before storing
    hashed_password = pwd_context.hash(password)
    new_employee = Employee(employee_id=employee_id, name=name, password=hashed_password)
    
    db.add(new_employee)
    db.commit()
    return {"message": "Employee added successfully"}

# Employee Login (Authentication)
@router.post("/api/authenticate/")
def authenticate_employee(employee_id: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Check if employee ID exists in database
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee ID not found")  # Employee does not exist

    # Verify password
    if not pwd_context.verify(password, employee.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")  # Incorrect password

    return {"message": "Login successful"}

@router.get("/api/get-employee/{employee_id}")
async def get_password(employee_id: str, db: Session = Depends(get_db)):
    # Fetch the employee from the database using the provided employee_id
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"employee_id": employee.employee_id, "password": employee.password}