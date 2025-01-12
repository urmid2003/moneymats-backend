from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Add a relationship to EnvelopData
    envelopes = relationship("EnvelopData", back_populates="user")

class EnvelopData(Base):
    __tablename__ = "envelop_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    envelope_name = Column(String, nullable=False)
    initial_amount = Column(Integer, nullable=False)
    remaining_amount = Column(Integer, nullable=False)

    # Define the back_populates relationship
    user = relationship("User", back_populates="envelopes")
