from pydantic import BaseModel
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# Login Schema
class LoginData(BaseModel):
    username: str
    password: str

# Patient Schemas
class PatientBase(BaseModel):
    user_id: int
    name: str
    age: int
    blood_group: str
    contact: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    class Config:
        from_attributes = True

# Doctor Schemas
class DoctorBase(BaseModel):
    user_id: int
    name: str
    specialization: str
    contact: str

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: int
    class Config:
        from_attributes = True

# Admin Schemas
class AdminBase(BaseModel):
    user_id: int

class AdminCreate(AdminBase):
    pass

class Admin(AdminBase):
    id: int
    class Config:
        from_attributes = True

# Medicine Schemas
class MedicineBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int

class MedicineCreate(MedicineBase):
    pass

class Medicine(MedicineBase):
    id: int
    class Config:
        from_attributes = True

# Prescription Schemas
class PrescriptionBase(BaseModel):
    doctor_id: int
    patient_id: int
    medicine_id: int
    dosage: str
    instructions: str

class PrescriptionCreate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    id: int
    doctor: Optional[Doctor] = None
    patient: Optional[Patient] = None
    medicine: Optional[Medicine] = None
    class Config:
        from_attributes = True

# Reservation Schemas
class ReservationBase(BaseModel):
    patient_id: int
    medicine_id: int
    quantity: int

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int
    status: str
    patient: Optional[Patient] = None
    medicine: Optional[Medicine] = None
    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    datetime: str
    status: str = "Pending"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: str

class Appointment(AppointmentBase):
    id: int
    patient: Optional[Patient] = None
    doctor: Optional[Doctor] = None
    class Config:
        from_attributes = True

# ClinicalRecord Schemas
class ClinicalRecordBase(BaseModel):
    patient_id: int
    doctor_id: int
    diagnosis_history: str
    vitals: str
    physician_notes: str

class ClinicalRecordCreate(ClinicalRecordBase):
    pass

class ClinicalRecord(ClinicalRecordBase):
    id: int
    patient: Optional[Patient] = None
    doctor: Optional[Doctor] = None
    class Config:
        from_attributes = True
