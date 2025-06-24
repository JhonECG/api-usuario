from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr

class Direccion(BaseModel):
    calle: str
    numero: str
    ciudad: str
    pais: str

class UsuarioBase(BaseModel):
    nombres: str
    apellidos: str
    email: EmailStr
    telefono: str
    direccion: Direccion

class UsuarioRegistro(UsuarioBase):
    password: str
    fecha_registro: datetime

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioOut(UsuarioBase):
    id: str
    fecha_registro: datetime
    rol: str

class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[Direccion] = None
    password: Optional[str] = None
