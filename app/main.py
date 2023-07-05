import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from hashlib import sha256
from typing import Optional
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, HTTPException, status, Query
import json
import hmac

app = FastAPI()

router = APIRouter(prefix="/tglogin")

BOT_TOKEN = '6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw'


@router.get('/')
def get_link(id: int, first_name: str, last_name: Optional[str], auth_date: int, hash: str, username: Optional[str] = Query(None),
             photo_url: Optional[str] = Query(None)):
    """Метод для авторизации через тг"""
    fields = dict(
        {"id": id, "first_name": first_name,"last_name": last_name, 'username': username, 'photo_url': photo_url, 'auth_date': auth_date,
         'hash': hash})
    hash = fields.pop('hash')
    auth_date = fields.get('auth_date')
    id = fields.get('id')
    fields = dict(sorted(fields.items(), key=lambda item: item[0]))
    data_check_string = ('\n'.join('='.join((key, str(val))) for (key, val) in fields.items()))
    secret = sha256(BOT_TOKEN.encode('utf-8'))
    sig = hmac.new(secret.digest(), data_check_string.encode('utf-8'), sha256).hexdigest()
    if sig == hash:
        response = RedirectResponse('/')
        response.set_cookie(key="token", value=hash)
        response.set_cookie(key="tg_uid", value=id)
        response.set_cookie(key="tg_uname", value=username)
        return response
    return "Error while logging in"


app.include_router(router, tags=['Telegram Login'])

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=False,
        workers=4
    )
