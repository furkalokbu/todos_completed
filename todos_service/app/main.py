from fastapi import FastAPI
from starlette import status
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from app.models import Base
from app.database import engine
from app.routers import todos, auth, users

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="app/static"), name='static')

@app.get('/')
async def root():
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(users.router)