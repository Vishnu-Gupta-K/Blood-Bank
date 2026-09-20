from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional

from models import User, Donor, ReceiverRequest, DonationRecord, BloodGroup
import schemas
from auth import get_password_hash

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Donor CRUD operations
def create_donor(db: Session, donor: schemas.DonorCreate, user_id: int):
    db_donor = Donor(
        user_id=user_id,
        name=donor.name,
        gender=donor.gender,
        phone_number=donor.phone_number,
        blood_group=donor.blood_group,
        state=donor.state,
        district=donor.district,
        village=donor.village,
        pincode=donor.pincode
    )
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor

def get_donor_by_id(db: Session, donor_id: int):
    return db.query(Donor).filter(Donor.id == donor_id).first()

def get_donor_by_user_id(db: Session, user_id: int):
    return db.query(Donor).filter(Donor.user_id == user_id).first()

def update_donor(db: Session, donor_id: int, donor_data: schemas.DonorUpdate):
    db_donor = get_donor_by_id(db, donor_id)
    if not db_donor:
        return None
    
    update_data = donor_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_donor, key, value)
    
    db.commit()
    db.refresh(db_donor)
    return db_donor

def search_donors(db: Session, search_params: schemas.DonorSearchParams):
    query = db.query(Donor)
    
    # Apply filters based on search parameters
    if search_params.blood_group:
        query = query.filter(Donor.blood_group == search_params.blood_group)
    if search_params.state:
        query = query.filter(Donor.state == search_params.state)
    if search_params.district:
        query = query.filter(Donor.district == search_params.district)
    if search_params.village:
        query = query.filter(Donor.village == search_params.village)
    if search_params.is_available is not None:
        query = query.filter(Donor.is_available == search_params.is_available)
    
    return query.all()

# Receiver Request CRUD operations
def create_receiver_request(db: Session, request: schemas.ReceiverRequestCreate, user_id: int):
    db_request = ReceiverRequest(
        user_id=user_id,
        blood_group_needed=request.blood_group_needed,
        state=request.state,
        district=request.district,
        village=request.village,
        urgency_level=request.urgency_level,
        notes=request.notes
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_receiver_request_by_id(db: Session, request_id: int):
    return db.query(ReceiverRequest).filter(ReceiverRequest.id == request_id).first()

def get_receiver_requests_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(ReceiverRequest).filter(ReceiverRequest.user_id == user_id).offset(skip).limit(limit).all()

def update_receiver_request(db: Session, request_id: int, request_data: schemas.ReceiverRequestUpdate):
    db_request = get_receiver_request_by_id(db, request_id)
    if not db_request:
        return None
    
    update_data = request_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_request, key, value)
    
    db.commit()
    db.refresh(db_request)
    return db_request

# Donation Record CRUD operations
def create_donation_record(db: Session, record: schemas.DonationRecordCreate):
    db_record = DonationRecord(
        donor_id=record.donor_id,
        receiver_request_id=record.receiver_request_id,
        quantity_ml=record.quantity_ml,
        notes=record.notes
    )
    db.add(db_record)
    
    # Update donor's last donation date
    donor = get_donor_by_id(db, record.donor_id)
    donor.last_donation_date = datetime.now()
    
    db.commit()
    db.refresh(db_record)
    return db_record

def get_donation_records_by_donor_id(db: Session, donor_id: int, skip: int = 0, limit: int = 100):
    return db.query(DonationRecord).filter(DonationRecord.donor_id == donor_id).offset(skip).limit(limit).all()

def get_donation_records_by_request_id(db: Session, request_id: int, skip: int = 0, limit: int = 100):
    return db.query(DonationRecord).filter(DonationRecord.receiver_request_id == request_id).offset(skip).limit(limit).all()