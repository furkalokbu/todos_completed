from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Annotated, Optional
from pydantic import BaseModel
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Users


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = '70625f34a50ea45a866a3cfc2d70e45481da2d8eee118cad1ebf29046d08ba71'
ALGORITHM = 'HS256'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory='app/templates')


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username : Optional[str] = None
        self.password : Optional[str] = None

    async def create_oath_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


async def get_current_user(request: Request):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            return None
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail='Could not validate user.')


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    print(form_data.username)
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False

    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, user.role, expires_delta=token_expires)

    response.set_cookie(key='access_token', value=token, httponly=True)

    return True


@router.get('/', response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_oath_form()
        response = RedirectResponse('/todos', status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = 'Incorrect Username or Password'
            return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})

        return response
    except HTTPException:
        msg = 'Unknown Error'
        return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})


@router.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        phone_number = create_user_request.phone_number,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )
    db.add(create_user_model)
    db.commit()
