from typing import Annotated
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import SessionLocal
from sqlalchemy.orm import Session

import app.models as models
from app.routers.auth import get_current_user

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

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()
    
    return templates.TemplateResponse('home.html', {'request': request, 'todos': todos})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('add-todo.html', {'request': request})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(db: db_dependency, request: Request, title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    
    model_todo = models.Todos()
    model_todo.title = title
    model_todo.description = description
    model_todo.priority = priority
    model_todo.complete = False
    model_todo.owner_id = user.get('id')

    db.add(model_todo)
    db.commit()

    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(db: db_dependency, request: Request, todo_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse('edit-todo.html', {'request': request, 'todo': todo})


@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo_commit(request:Request, db: db_dependency, todo_id: int, title: str = Form(...), 
                           description: str = Form(...), priority: int = Form(...)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse('/todos', status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}')
async def delete_todo(request: Request, db: db_dependency, todo_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
                 .filter(models.Todos.owner_id == user.get('id')).first()
    
    if todo_model is None:
        return RedirectResponse('/todos', status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return RedirectResponse('/todos', status_code=status.HTTP_302_FOUND)


@router.get('/complete/{todo_id}')
async def complete_todo(request: Request, db: db_dependency, todo_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse('/todos', status_code=status.HTTP_302_FOUND)
