from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.database import engine, get_db

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Management System API")

# Setup default admin if none exists
def create_default_admin():
    db = next(get_db())
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user:
        new_user = models.User(username="admin", password="password", role="admin")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        new_admin = models.Admin(user_id=new_user.id)
        db.add(new_admin)
        db.commit()

@app.on_event("startup")
def startup_event():
    create_default_admin()

# --- AUTH / LOGIN ---
@app.post("/login/")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username, models.User.password == data.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Return user details + specific profile ID
    profile_id = None
    if user.role == "admin" and user.admin_profile:
        profile_id = user.admin_profile.id
    elif user.role == "doctor" and user.doctor_profile:
        profile_id = user.doctor_profile.id
    elif user.role == "patient" and user.patient_profile:
        profile_id = user.patient_profile.id
        
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "profile_id": profile_id
    }

# --- USERS ---

from pydantic import BaseModel
class PasswordUpdate(BaseModel):
    password: str

@app.put("/users/{user_id}/password")
def update_password(user_id: int, data: PasswordUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # In a real system, hash the password! (For mock purposes, storing plain text)
    user.password = data.password
    db.commit()
    return {"msg": "Password updated successfully"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = models.User(username=user.username, password=user.password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": "User deleted"}


# --- PATIENTS ---
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Patient).offset(skip).limit(limit).all()

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

# --- DOCTORS ---
@app.post("/doctors/", response_model=schemas.Doctor)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = models.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@app.get("/doctors/", response_model=List[schemas.Doctor])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Doctor).offset(skip).limit(limit).all()

@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

# --- MEDICINES ---
@app.post("/medicines/", response_model=schemas.Medicine)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    db_medicine = models.Medicine(**medicine.model_dump())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@app.get("/medicines/", response_model=List[schemas.Medicine])
def read_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Medicine).offset(skip).limit(limit).all()

# --- PRESCRIPTIONS ---
@app.post("/prescriptions/", response_model=schemas.Prescription)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = models.Prescription(**prescription.model_dump())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

@app.get("/prescriptions/", response_model=List[schemas.Prescription])
def read_prescriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Prescription).offset(skip).limit(limit).all()

# --- RESERVATIONS ---
@app.post("/reservations/", response_model=schemas.Reservation)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == reservation.medicine_id).first()
    if not medicine or medicine.stock_quantity < reservation.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    medicine.stock_quantity -= reservation.quantity
    
    db_reservation = models.Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@app.get("/reservations/", response_model=List[schemas.Reservation])
def read_reservations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Reservation).offset(skip).limit(limit).all()

# --- APPOINTMENTS ---
@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_app = models.Appointment(**appointment.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Appointment).offset(skip).limit(limit).all()

@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, app_update: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_app.status = app_update.status
    db.commit()
    db.refresh(db_app)
    return db_app

# --- CLINICAL RECORDS (EHR) ---
@app.post("/records/", response_model=schemas.ClinicalRecord)
def create_record(record: schemas.ClinicalRecordCreate, db: Session = Depends(get_db)):
    db_record = models.ClinicalRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/", response_model=List[schemas.ClinicalRecord])
def read_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.ClinicalRecord).offset(skip).limit(limit).all()


# --- BEDS ---
@app.post("/beds/", response_model=schemas.Bed)
def create_bed(bed: schemas.BedCreate, db: Session = Depends(get_db)):
    db_bed = models.Bed(**bed.model_dump())
    db.add(db_bed)
    db.commit()
    db.refresh(db_bed)
    return db_bed

@app.get("/beds/", response_model=List[schemas.Bed])
def read_beds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Bed).offset(skip).limit(limit).all()

@app.put("/beds/{bed_id}", response_model=schemas.Bed)
def update_bed(bed_id: int, bed: schemas.BedCreate, db: Session = Depends(get_db)):
    db_bed = db.query(models.Bed).filter(models.Bed.id == bed_id).first()
    if not db_bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    
    db_bed.status = bed.status
    db_bed.patient_id = bed.patient_id
    db.commit()
    db.refresh(db_bed)
    return db_bed

# --- INVOICES ---
@app.post("/invoices/", response_model=schemas.Invoice)
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = models.Invoice(**invoice.model_dump())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@app.get("/invoices/", response_model=List[schemas.Invoice])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Invoice).offset(skip).limit(limit).all()

@app.put("/invoices/{invoice_id}/pay", response_model=schemas.Invoice)
def pay_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    db_invoice.status = "Paid"
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# --- MESSAGES ---
@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_msg = models.Message(**message.model_dump())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

@app.get("/messages/", response_model=List[schemas.Message])
def read_messages(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return db.query(models.Message).offset(skip).limit(limit).all()

# --- AUDITS ---
@app.post("/audits/", response_model=schemas.AuditLog)
def create_audit(audit: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    db_audit = models.AuditLog(**audit.model_dump())
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

@app.get("/audits/", response_model=List[schemas.AuditLog])
def read_audits(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    return db.query(models.AuditLog).order_by(models.AuditLog.id.desc()).offset(skip).limit(limit).all()
