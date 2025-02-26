from fastapi import FastAPI
from routes import faculty, attendance, employee

app = FastAPI(title="Faculty Attendance System")

# Include routers
app.include_router(faculty.router, prefix="/api/faculty", tags=["Faculty"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(employee.router, prefix="/api/employee", tags=["Employee"])

@app.get("/")
def home():
    return {"message": "Welcome to the Intelligent Attendance System"}
