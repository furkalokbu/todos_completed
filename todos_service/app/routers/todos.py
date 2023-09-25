from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import SessoinLocal
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/todos',
    tags=['todos'],
    responses={404: {'description': 'Not found'}}
)

def get_db():
    db = SessoinLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory='app/templates')
db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', response_class=HTMLResponse)
async def read_all_by_user(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse('add-todo.html', {'request': request})


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(request: Request):
    return templates.TemplateResponse('edit-todo.html', {'request': request})
