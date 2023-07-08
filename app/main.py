import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from hashlib import sha256
from typing import Optional
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, HTTPException, status, Query
import json
import hmac
import html

from pydantic import Field

from database.database_manager import db_score
from fastapi.responses import Response
import jinja2
from fastapi.templating import Jinja2Templates
from fastapi import Request
from database.database_manager import db_history_allview
from database.database_manager import db_history_view
from database.database_manager import db_receive_date
from database.database_manager import db_admin

app = FastAPI()

templates = Jinja2Templates(directory="../app/templates")

router = APIRouter(prefix="/tglogin")

BOT_TOKEN = '6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw'


@router.get('/')
def get_link(id: int, first_name: str, last_name: Optional[str], auth_date: int, hash: str,
             username: Optional[str] = Query(None),
             photo_url: Optional[str] = Query(None)):
    """Метод для авторизации через тг"""
    fields = dict(
        {"id": id, "first_name": first_name, "last_name": last_name, 'username': username, 'photo_url': photo_url,
         'auth_date': auth_date,
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


@router.get("/{id}")
def get_balance(id):
    return db_score(id)


@app.get("/")
def root_page(request: Request):
    telegram_token = request.cookies.get('token')
    telegram_id = request.cookies.get('tg_uid')
    if telegram_id is None and telegram_token is None:
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )
    else:
        return RedirectResponse('/user')


@app.get("/user")
def main_page(request: Request):
    telegram_token = request.cookies.get('token')
    telegram_id = request.cookies.get('tg_uid')
    if telegram_id is None and telegram_token is None:
        return RedirectResponse('/')
    else:
        dates = db_receive_date(telegram_id)
        return templates.TemplateResponse(
            "user.html",
            {"request": request,
             "dates": dates},
        )


@app.get("/logout")
def logout_page():
    redirect = RedirectResponse('/')
    redirect.delete_cookie("token")
    redirect.delete_cookie("tg_uid")
    return redirect


@app.get("/history")
def history_page(request: Request, date_from: str | None = Query(default=None), date_to: str | None= Query(default=None)):
    telegram_token = request.cookies.get('token')
    telegram_id = request.cookies.get('tg_uid')
    if date_from is None or date_to is None:
        all_history = db_history_allview(user_id=telegram_id)
    elif date_from is not None and date_to is not None:
        all_history = db_history_view(user_id=telegram_id, date_mes=(date_from, date_to))

    if telegram_id is None and telegram_token is None:
        return RedirectResponse('/')
    else:
        return templates.TemplateResponse(
            "history.html",
            {"request": request, "all_history": all_history},
        )

@app.get("/admin")
def admin_page(request:Request):
    telegram_token = request.cookies.get('token')
    telegram_id = request.cookies.get('tg_uid')
    check_admin = db_admin(user_id=telegram_id)
    if telegram_id is None and telegram_token is None:
        return RedirectResponse('/')
    elif check_admin[0]:
        return templates.TemplateResponse(
            "admin.html",
            {"request": request,"check_admin":check_admin},
        )

#
# @router.get('/balance')
# def get_balance()


app.include_router(router, tags=['Telegram Login'])

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=False,
        workers=4
    )
