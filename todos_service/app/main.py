from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.routers import todos

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name='static')

app.include_router(todos.router)
