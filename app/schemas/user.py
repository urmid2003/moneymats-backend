from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True

class EnvelopDataResponse(BaseModel):
    id: int
    user_id: int
    envelope_name: str
    initial_amount: float
    remaining_amount: float

    class Config:
        orm_mode = True

class EnvelopeCreate(BaseModel):
    envelope_name: str
    initial_amount: int

    class Config:
        orm_mode = True

