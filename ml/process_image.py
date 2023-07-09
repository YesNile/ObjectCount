import os
from time import sleep

import cv2
import numpy as np
from ultralytics import YOLO
from celery import Celery
from database.database_manager import update_zip_path

from utils.utils import create_zip_archive

celery = Celery('tasks', broker='redis://localhost:6379',backend='redis://localhost:6379/0',result_extended=True, CELERY_TASK_TRACK_STARTED = True)


@celery.task()
def connect_to_web(path, a):
    print (os.getcwd())
    i = celery.control.inspect()
    print(i.scheduled)
    test = SegmentationModule(r"../best_with_badges.pt")
    sleep(5)
    web_work = test.segment_image(image_path=path, photo_id=str(a))
    message = f"Количество найденных объектов на фотографии: {len(web_work[0])}"
    update_zip_path(path,message, web_work[1])
    return web_work[1]


class SegmentationModule:
    def __init__(self, model: str):
        # Инициализация модели YOLO
        self.model = YOLO(model)

    # def segment_image(self, image_path, photo_id):
    #     SegmentationModule.segment_image(modelka = self, image_path = image_path, photo_id = photo_id)

    def segment_image(self, image_path, photo_id):
        # Создание директории для сохранения результатов сегментации
        os.makedirs(rf"../images/{photo_id}", exist_ok=True)

        # Загрузка изображения
        img = cv2.imread(image_path)
        print(img)

        # Выполнение сегментации с помощью модели YOLO
        results = self.model(img)

        # Список путей к сегментированным изображениям
        segmented_images = []

        if results[0].masks is not None:
            for i in range(len(results[0].masks)):
                # Обработка маски для создания прозрачных изображений
                mask_raw = results[0].masks[i].cpu().data.numpy().transpose(1, 2, 0)
                mask_4channel = cv2.merge((mask_raw, mask_raw, mask_raw, mask_raw))
                h2, w2, c2 = results[0].orig_img.shape
                mask = cv2.resize(mask_4channel, (w2, h2))
                bgra = cv2.cvtColor(mask, cv2.COLOR_BGR2BGRA)
                bgra[:, :, 3] = np.where((bgra[:, :, :3] > 0).any(2), 255, 0)

                # Обрезка сегментированных изображений
                img_resized = cv2.resize(results[0].orig_img, (w2, h2))
                img_resized = img_resized[:h2, :w2]
                mask = bgra[:, :, 3]
                _, mask_binary = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
                img_resized = img_resized.astype(np.uint8)
                mask_binary = mask_binary.astype(np.uint8)
                masked = cv2.bitwise_and(img_resized, img_resized, mask=mask_binary)
                transparent = np.zeros((h2, w2, 4), dtype=np.uint8)
                transparent[:, :, :3] = masked
                transparent[:, :, 3] = mask_binary

                # Поиск контуров и обрезка изображения
                contours, _ = cv2.findContours(
                    mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                x, y, w, h = cv2.boundingRect(contours[0])
                cropped = masked[y: y + h, x: x + w]
                cropped_transparent = transparent[y: y + h, x: x + w]

                # Сохранение сегментированных изображений в отдельные файлы
                segment_path = (
                    rf"../images/{photo_id}/object_{i}.png"
                )
                cv2.imwrite(segment_path, cropped_transparent)
                segmented_images.append(segment_path)

                # Сохранение обработанного изображения с наложенными масками
                self.save_segmented_res(results, photo_id)
        zip = self.save_zip_archive(photo_id)

        return (segmented_images, zip)

    def save_segmented_res(self, results, photo_id):
        # Создание пути к сохраняемому изображению
        res_plotted = results[0].plot()
        image_path = rf"../images/{photo_id}.jpg"

        # Сохранение обработанного изображения
        cv2.imwrite(image_path, res_plotted)

    def save_zip_archive(self,photo_id):

        # Создание директории с сегментированными изображениями
        directory = rf"../images/{photo_id}"

        # Создание ZIP-архива с сегментированными изображениями
        output_path = rf"../images/{photo_id}.zip"
        create_zip_archive(directory, output_path)
        return output_path
