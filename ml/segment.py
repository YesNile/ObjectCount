import cv2
from ultralytics import YOLO
import numpy as np

# Load the image
img = cv2.imread("./image.jpg")

# Create the YOLOv8 model
model = YOLO("yolov8l-seg.pt")

results = model(img)

if results[0].masks is not None:
    for i in range(len(results[0].masks)):
        # Convert mask to single channel image
        mask_raw = results[0].masks[i].cpu().data.numpy().transpose(1, 2, 0)

        # Convert single channel grayscale to 4 channel image (BGR + Alpha)
        mask_4channel = cv2.merge((mask_raw, mask_raw, mask_raw, mask_raw))

        # Get the size of the original image (height, width, channels)
        h2, w2, c2 = results[0].orig_img.shape

        # Resize the mask to the same size as the image (can probably be removed if image is the same size as the model)
        mask = cv2.resize(mask_4channel, (w2, h2))

        # Convert BGR to BGRA
        bgra = cv2.cvtColor(mask, cv2.COLOR_BGR2BGRA)

        # Set transparent pixels to 0 (background)
        bgra[:, :, 3] = np.where((bgra[:, :, :3] > 0).any(2), 255, 0)

        # Resize the original image to match the size of the mask
        img_resized = cv2.resize(results[0].orig_img, (w2, h2))

        # Ensure both images have the same dimensions
        img_resized = img_resized[:h2, :w2]

        # Create a mask from the alpha channel
        mask = bgra[:, :, 3]

        # Convert the mask to a binary mask
        _, mask_binary = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
        
        # Convert the data type of img_resized and mask_binary to np.uint8
        img_resized = img_resized.astype(np.uint8)
        mask_binary = mask_binary.astype(np.uint8)

        # Apply the binary mask to the resized original image
        masked = cv2.bitwise_and(img_resized, img_resized, mask=mask_binary)

        # Find contours of the object
        contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the bounding box of the object
        x, y, w, h = cv2.boundingRect(contours[0])

        # Crop the image to the bounding box of the object
        cropped = masked[y:y+h, x:x+w]

        # Save the cropped image
        cv2.imwrite(f"results_{i}.png", cropped)
