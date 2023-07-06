import os
import cv2
import numpy as np
from ultralytics import YOLO
import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, status, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from hashlib import sha256
import hmac
from typing import Optional
from ml.segment import segment_image

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/tglogin")

BOT_TOKEN = '6273302502:AAGGO3PgrLDwIG9mqwUOU-nSQ3yWuWWVtYw'

model = YOLO("./best.pt")

@router.post('/')  # Use POST instead of GET for form submission
async def get_link(
    id: int,
    first_name: str,
    last_name: Optional[str],
    auth_date: int,
    hash: str,
    request: Request,
    username: Optional[str] = Query(None),
    photo_url: Optional[str] = Query(None)
):
    fields = dict(
        {
            "id": id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            'photo_url': photo_url,
            'auth_date': auth_date,
            'hash': hash
        }
    )
    hash = fields.pop('hash')
    auth_date = fields.get('auth_date')
    id = fields.get('id')
    fields = dict(sorted(fields.items(), key=lambda item: item[0]))
    data_check_string = '\n'.join('='.join((key, str(val))) for key, val in fields.items())
    secret = sha256(BOT_TOKEN.encode('utf-8'))
    sig = hmac.new(secret.digest(), data_check_string.encode('utf-8'), sha256).hexdigest()
    if sig == hash:
        response = RedirectResponse('/')
        response.set_cookie(key="token", value=hash)
        response.set_cookie(key="tg_uid", value=str(id))
        response.set_cookie(key="tg_uname", value=username)

        # Получение пути загруженного изображения
        form_data = await request.form()
        image = form_data["image"]
        image_path = f"./images/{image.filename}.jpg"
        with open(image_path, "wb") as f:
            f.write(await image.read())  # Use await to read the file data

        segmented_images = segment_image(image_path, model, id)

        # Возврат шаблона сегментированных изображений и других переменных
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "segmented_images": segmented_images},
        )
    return "Error while logging in"

app.include_router(router, tags=['Telegram Login'])
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=False,
        workers=4
    )
