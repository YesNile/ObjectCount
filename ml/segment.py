import cv2
from ultralytics import YOLO
import numpy as np

# Load the image
img = cv2.imread("./image.jpg")

# Create the YOLOv8 model
model = YOLO("yolov8l-seg.pt")

results = model(img)

if(results[0].masks is not None):
    for i in range(len(results[0].masks)):
        # Conver`t mask to single channel image
        mask_raw = results[0].masks[i].cpu().data.numpy().transpose(1, 2, 0)
        
        # Convert single channel grayscale to 3 channel image
        mask_3channel = cv2.merge((mask_raw,mask_raw,mask_raw))

        # Get the size of the original image (height, width, channels)
        h2, w2, c2 = results[0].orig_img.shape
        
        # Resize the mask to the same size as the image (can probably be removed if image is the same size as the model)
        mask = cv2.resize(mask_3channel, (w2, h2))

        # Convert BGR to HSV
        hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)

        # Define range of brightness in HSV
        lower_black = np.array([0,0,0])
        upper_black = np.array([0,0,1])

        # Create a mask. Threshold the HSV image to get everything black
        mask = cv2.inRange(mask, lower_black, upper_black)

        # Invert the mask to get everything but black
        mask = cv2.bitwise_not(mask)

        # Apply the mask to the original image
        masked = cv2.bitwise_and(results[0].orig_img, results[0].orig_img, mask=mask)

        # Show the masked part of the image
        cv2.imwrite(f"results_{i}.jpg", masked)