import os
import cv2
import numpy as np
from ultralytics import YOLO
import zipfile
import os


def create_zip_archive(directory, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))

def segment_image(image_path, model, photo_id):
    os.makedirs(f"./images/{photo_id}", exist_ok=True)
    img = cv2.imread(image_path)
    results = model(img)
    segmented_images = []
    if results[0].masks is not None:
        for i in range(len(results[0].masks)):
            mask_raw = results[0].masks[i].cpu().data.numpy().transpose(1, 2, 0)
            mask_4channel = cv2.merge((mask_raw, mask_raw, mask_raw, mask_raw))
            h2, w2, c2 = results[0].orig_img.shape
            mask = cv2.resize(mask_4channel, (w2, h2))
            bgra = cv2.cvtColor(mask, cv2.COLOR_BGR2BGRA)
            bgra[:, :, 3] = np.where((bgra[:, :, :3] > 0).any(2), 255, 0)
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
            contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            x, y, w, h = cv2.boundingRect(contours[0])
            cropped = masked[y:y+h, x:x+w]
            cropped_transparent = transparent[y:y+h, x:x+w]
            segment_path = f"./images/{photo_id}/object_{i}.png"
            cv2.imwrite(segment_path, cropped_transparent)
            segmented_images.append(segment_path)
            
    res_plotted = results[0].plot()
    cv2.imwrite(f"{photo_id}.jpg", res_plotted)
    directory = f"./images/{photo_id}"  
    output_path = f"{photo_id}.zip"
    create_zip_archive(directory, output_path)

    return segmented_images
