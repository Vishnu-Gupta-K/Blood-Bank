from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv

# Import local modules
from database import engine, get_db, Base
import models
import schemas
import crud
from auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from pdf_generator import generate_donor_list_pdf

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Blood Bank Application"),
    description="API for Blood Bank Application",
    version=os.getenv("APP_VERSION", "1.0.0")
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Blood Bank API"}

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints
@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

# Donor endpoints
@app.post("/donors/", response_model=schemas.DonorResponse)
async def create_donor_profile(donor: schemas.DonorCreate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if user already has a donor profile
    db_donor = crud.get_donor_by_user_id(db, user_id=current_user.id)
    if db_donor:
        raise HTTPException(status_code=400, detail="User already has a donor profile")
    
    return crud.create_donor(db=db, donor=donor, user_id=current_user.id)

@app.get("/donors/me/", response_model=schemas.DonorResponse)
async def read_donor_me(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_donor = crud.get_donor_by_user_id(db, user_id=current_user.id)
    if db_donor is None:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    return db_donor

@app.put("/donors/me/", response_model=schemas.DonorResponse)
async def update_donor_me(donor: schemas.DonorUpdate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_donor = crud.get_donor_by_user_id(db, user_id=current_user.id)
    if db_donor is None:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    
    return crud.update_donor(db=db, donor_id=db_donor.id, donor_data=donor)

@app.get("/donors/search/", response_model=List[schemas.DonorResponse])
async def search_donors(search_params: schemas.DonorSearchParams = Depends(), db: Session = Depends(get_db)):
    donors = crud.search_donors(db, search_params=search_params)
    return donors

# Receiver Request endpoints
@app.post("/receiver-requests/", response_model=schemas.ReceiverRequestResponse)
async def create_receiver_request(request: schemas.ReceiverRequestCreate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return crud.create_receiver_request(db=db, request=request, user_id=current_user.id)

@app.get("/receiver-requests/", response_model=List[schemas.ReceiverRequestResponse])
async def read_receiver_requests(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    requests = crud.get_receiver_requests_by_user_id(db, user_id=current_user.id, skip=skip, limit=limit)
    return requests

@app.get("/receiver-requests/{request_id}", response_model=schemas.ReceiverRequestResponse)
async def read_receiver_request(request_id: int, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_request = crud.get_receiver_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    if db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this request")
    return db_request

@app.put("/receiver-requests/{request_id}", response_model=schemas.ReceiverRequestResponse)
async def update_receiver_request(request_id: int, request_data: schemas.ReceiverRequestUpdate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_request = crud.get_receiver_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    if db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this request")
    
    return crud.update_receiver_request(db=db, request_id=request_id, request_data=request_data)

# Donation Record endpoints
@app.post("/donation-records/", response_model=schemas.DonationRecordResponse)
async def create_donation_record(record: schemas.DonationRecordCreate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Verify donor exists
    donor = crud.get_donor_by_id(db, donor_id=record.donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    # If receiver request is provided, verify it exists
    if record.receiver_request_id:
        request = crud.get_receiver_request_by_id(db, request_id=record.receiver_request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Receiver request not found")
    
    return crud.create_donation_record(db=db, record=record)

@app.get("/donation-records/donor/{donor_id}", response_model=List[schemas.DonationRecordResponse])
async def read_donation_records_by_donor(donor_id: int, skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Verify donor exists
    donor = crud.get_donor_by_id(db, donor_id=donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    records = crud.get_donation_records_by_donor_id(db, donor_id=donor_id, skip=skip, limit=limit)
    return records

# PDF Export endpoint
@app.post("/export/donors-pdf/")
async def export_donors_pdf(export_params: schemas.PDFExportParams, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Generate PDF
    pdf_buffer = generate_donor_list_pdf(
        db=db,
        donor_ids=export_params.donor_ids,
        title=export_params.title,
        include_contact_info=export_params.include_contact_info
    )
    
    # Return PDF as a downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=donor_list_{current_user.id}_{int(datetime.now().timestamp())}.pdf"
        }
    )