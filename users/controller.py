from fastapi import APIRouter, Depends, HTTPException
import jwt
from sqlalchemy.orm import Session
from typing import List
from . import schemas, service, models
from .schemas import AddressCreate, Address
from core.database import get_db


router = APIRouter()

@router.get("/addresses", response_model=List[Address])
def get_all_addresses(db: Session = Depends(get_db)):
    return db.query(models.Address).all()# ---------------- LEER USUARIO ----------------
@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return service.get_user(db, user_id)

# ---------------- LEER TODOS LOS USUARIOS ----------------
@router.get("", response_model=List[schemas.User])
def get_users(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Page and size must be greater than 0")
    
    skip = (page - 1) * size
    return service.get_users(db, skip, size)

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    current_user_role = "admin"  # Este valor debería ser dinámico según el usuario autenticado
    return service.update_user(db, user_id, user_update, current_user_role)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return service.delete_user(db, user_id)

# ---------------- AÑADIR O ACTUALIZAR DIRECCIÓN ----------------
@router.post("/{user_id}/address", response_model=Address)
def add_or_update_address(user_id: int, address_data: AddressCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_address = db.query(models.Address).filter(models.Address.user_id == user_id).first()
    if existing_address:
        existing_address.street = address_data.street
        existing_address.city = address_data.city
        existing_address.country = address_data.country
        existing_address.postal_code = address_data.postal_code
    else:
        new_address = models.Address(
            user_id=user_id,
            street=address_data.street,
            city=address_data.city,
            country=address_data.country,
            postal_code=address_data.postal_code
        )
        db.add(new_address)

    db.commit()
    db.refresh(existing_address if existing_address else new_address)

    return existing_address if existing_address else new_address

@router.get("/addresses/{address_id}", response_model=Address)
def get_address_by_id(address_id: int, db: Session = Depends(get_db)):
    return db.query(models.Address).filter(models.Address.id == address_id).first()

@router.put("/addresses/{address_id}", response_model=Address)
def update_address(address_id: int, address_update: AddressCreate, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    for field, value in address_update.dict().items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address

@router.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}

#------------------------Verificar autenticación--------------1----------
@router.post("/verify-token")
def verify_token(token: str):
    try:
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        return {"valid": True, "user_id": payload.get("sub")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
