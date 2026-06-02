"""
Simple Face Detection - Jyotipriya Panda
Reg. No. 2407432009 | M.Tech CSE 2024-2026 | GIFT Bhubaneswar
Supervisor: Asst. Prof. Mohapatra Girashree Shau
"""

import cv2
import sys

# Load Haar cascade (built into OpenCV - no extra install needed)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
)

# ── MODE: pass an image path as argument, or leave empty for webcam ──────────
IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else None


def detect_on_image(path):
    img = cv2.imread(path)
    if img is None:
        print(f"Could not open image: {path}")
        return
    faces = detect(img)
    draw(img, faces)
    print(f"Detected {len(faces)} face(s) in {path}")
    cv2.imshow("Face Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def detect_on_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam. Try passing an image path instead:")
        print("  python detect_face.py photo.jpg")
        return
    print("Webcam running — press Q to quit")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            faces = detect(frame)
            draw(frame, faces)
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Stopped.")


def detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    return face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40)
    )


def draw(img, faces):
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, "Face", (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


if IMAGE_PATH:
    detect_on_image(IMAGE_PATH)
else:
    detect_on_webcam()
