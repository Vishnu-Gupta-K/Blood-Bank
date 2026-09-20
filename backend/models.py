from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    
    # This method ensures the enum value is used when converting to SQL
    def _serialize_to_db(self):
        return self.value

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    donor_profile = relationship("Donor", back_populates="user", uselist=False)
    receiver_requests = relationship("ReceiverRequest", back_populates="user")

class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    gender = Column(Enum(Gender, values_callable=lambda obj: [e.value for e in obj]))
    phone_number = Column(String(20))
    blood_group = Column(Enum(BloodGroup, values_callable=lambda obj: [e.value for e in obj]))
    state = Column(String(50))
    district = Column(String(50))
    village = Column(String(50))
    pincode = Column(String(10))
    is_available = Column(Boolean, default=True)
    last_donation_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="donor_profile")
    donation_history = relationship("DonationRecord", back_populates="donor")

class ReceiverRequest(Base):
    __tablename__ = "receiver_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blood_group_needed = Column(Enum(BloodGroup, values_callable=lambda obj: [e.value for e in obj]))
    state = Column(String(50))
    district = Column(String(50))
    village = Column(String(50))
    urgency_level = Column(Integer, default=1)  # 1-5 scale, 5 being most urgent
    request_status = Column(String(20), default="pending")  # pending, fulfilled, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="receiver_requests")

class DonationRecord(Base):
    __tablename__ = "donation_records"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id"))
    receiver_request_id = Column(Integer, ForeignKey("receiver_requests.id"), nullable=True)
    donation_date = Column(DateTime(timezone=True), server_default=func.now())
    quantity_ml = Column(Integer, default=450)  # Standard blood donation is about 450ml
    notes = Column(Text, nullable=True)
    
    # Relationships
    donor = relationship("Donor", back_populates="donation_history")
    receiver_request = relationship("ReceiverRequest")