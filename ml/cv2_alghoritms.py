import os
import cv2 

output_dir = "objects_resize600400_thresh7000"
os.makedirs(output_dir, exist_ok=True)

for image in os.listdir("to_test_2"):
    final_path = f"{output_dir}/{image.split('.')[0]}"
    os.makedirs(final_path, exist_ok=True)

    # Загрузка изображения стола
    image = cv2.imread(f"to_test_2/{image}")

    # Получение разрешения изображения
    height, width, channels = image.shape
    print(f"Разрешение исходного изображения: {width}x{height}")

    if width > 1920 or height > 1080:
        desired_width = 600
        desired_height = 400
        resized_image = cv2.resize(image, (desired_width, desired_height))

    # перевод в серый
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # удаление шума
    denoised = cv2.medianBlur(gray, 5)

    # применение адаптивного порогового преобразования
    threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)

    # заполнение маленьких пробелов в предметах
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

    # поиск контуров на изображении
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # фильтрация контуров по площади
    min_area_threshold = 7000
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area_threshold]

    # вырезка и сохранение
    for i, contour in enumerate(filtered_contours):
        x, y, w, h = cv2.boundingRect(contour)
        object_image = image[y:y+h, x:x+w]
        filename = os.path.join(final_path, f'object_{i+1}.jpg')
        cv2.imwrite(filename, object_image)
        print(f"Вырезанный объект {i+1} сохранен: {filename}")
