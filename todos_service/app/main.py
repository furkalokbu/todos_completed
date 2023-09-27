from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.models import Base
from app.database import engine
from app.routers import todos, auth

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="app/static"), name='static')

app.include_router(todos.router)
app.include_router(auth.router)
