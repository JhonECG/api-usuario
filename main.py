from fastapi import FastAPI
from auth.controller import router as auth_router
from users.controller import router as users_router
from core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
