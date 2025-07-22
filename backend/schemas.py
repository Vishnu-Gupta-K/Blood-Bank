from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from models import Gender, BloodGroup

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

# Donor schemas
class DonorBase(BaseModel):
    name: str
    gender: Gender
    phone_number: str
    blood_group: BloodGroup
    state: str
    district: str
    village: str
    pincode: str

class DonorCreate(DonorBase):
    pass

class DonorUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[Gender] = None
    phone_number: Optional[str] = None
    blood_group: Optional[BloodGroup] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None
    is_available: Optional[bool] = None
    last_donation_date: Optional[datetime] = None

class DonorResponse(DonorBase):
    id: int
    user_id: int
    is_available: bool
    last_donation_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Receiver Request schemas
class ReceiverRequestBase(BaseModel):
    blood_group_needed: BloodGroup
    state: str
    district: str
    village: str
    urgency_level: Optional[int] = Field(1, ge=1, le=5)
    notes: Optional[str] = None

class ReceiverRequestCreate(ReceiverRequestBase):
    pass

class ReceiverRequestUpdate(BaseModel):
    blood_group_needed: Optional[BloodGroup] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    urgency_level: Optional[int] = Field(None, ge=1, le=5)
    request_status: Optional[str] = None
    notes: Optional[str] = None

class ReceiverRequestResponse(ReceiverRequestBase):
    id: int
    user_id: int
    request_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Donation Record schemas
class DonationRecordBase(BaseModel):
    donor_id: int
    receiver_request_id: Optional[int] = None
    quantity_ml: Optional[int] = 450
    notes: Optional[str] = None

class DonationRecordCreate(DonationRecordBase):
    pass

class DonationRecordResponse(DonationRecordBase):
    id: int
    donation_date: datetime

    class Config:
        from_attributes = True

# Search schemas
class DonorSearchParams(BaseModel):
    blood_group: Optional[BloodGroup] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    is_available: Optional[bool] = True

# PDF Export schema
class PDFExportParams(BaseModel):
    donor_ids: List[int]
    title: Optional[str] = "Donor List"
    include_contact_info: Optional[bool] = True