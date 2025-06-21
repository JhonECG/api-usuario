from pydantic import BaseModel
from typing import Optional

# -------- User Schemas --------
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    role: str
    username: str

    class Config:
        orm_mode = True

class UserOut(UserBase):
    id: int
    role: str
    username: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


# -------- Address Schemas --------
class AddressBase(BaseModel):
    country: str
    city: str
    street: str
    postal_code: Optional[str] = None

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None

class Address(AddressBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
