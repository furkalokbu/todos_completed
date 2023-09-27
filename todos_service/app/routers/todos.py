from typing import Annotated
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import SessionLocal
from sqlalchemy.orm import Session
import app.models as models


router = APIRouter(
    prefix='/todos',
    tags=['todos'],
    responses={404: {'description': 'Not found'}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory='app/templates')
db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: db_dependency):
    todos = db.query(models.Todos).filter(models.Todos.owner_id == 1).all()
    return templates.TemplateResponse('home.html', {'request': request, 'todos': todos})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse('add-todo.html', {'request': request})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(db: db_dependency, request: Request, title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...)):
    model_todo = models.Todos()
    model_todo.title = title
    model_todo.description = description
    model_todo.priority = priority
    model_todo.complete = False
    model_todo.owner_id = 1

    db.add(model_todo)
    db.commit()

    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(db: db_dependency, request: Request, todo_id: int):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse('edit-todo.html', {'request': request, 'todo': todo})
