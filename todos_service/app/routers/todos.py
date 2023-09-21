from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/todos',
    tags=['todos'],
    responses={404: {'description': 'Not found'}}
)

templates = Jinja2Templates(directory='app/templates')

@router.get('/test')
async def test(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})
