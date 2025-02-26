from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base

class Faculty(Base):
    __tablename__ = "faculty"
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    image = Column(LargeBinary, nullable=False)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    login_time = Column(String(20), nullable=True)
    logout_time = Column(String(20), nullable=True)
    date = Column(String(20), nullable=False)

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
