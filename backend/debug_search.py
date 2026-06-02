"""Debug script: test face search matching pipeline end-to-end."""
import sys, cv2, numpy as np, base64
sys.path.insert(0, '..')

from database import get_all_persons, get_all_embeddings

cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(img):
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
    return faces if len(faces) > 0 else []

def detect_faces_relaxed(img):
    """Lower threshold for smaller/thumbnail images."""
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.05, 3, minSize=(20, 20))
    return faces if len(faces) > 0 else []

def embedding(img, x, y, w, h):
    face = img[max(0,y):y+h, max(0,x):x+w]
    face = cv2.resize(face, (64, 64))
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [416], [0, 256])
    return cv2.normalize(hist, hist).flatten().astype(np.float32)

def cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0: return 0.0
    return float(np.dot(a / na, b / nb))

enrolled = get_all_embeddings()
persons  = get_all_persons()
print("Enrolled persons:", [e['name'] for e in enrolled])
print()

for p in persons:
    photo = p.get('photo_b64', '')
    if not photo:
        print(f"[{p['name']}] No stored photo - SKIP")
        continue

    _, _, data = photo.partition(',')
    raw = base64.b64decode(data)
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    print(f"--- Self-match test: {p['name']} ---")
    print(f"  Image size: {img.shape}")

    # Try strict detection first
    faces = detect_faces(img)
    print(f"  Strict detection (minSize=60): {len(faces)} face(s)")

    # Try relaxed if none found
    if len(faces) == 0:
        faces = detect_faces_relaxed(img)
        print(f"  Relaxed detection (minSize=20): {len(faces)} face(s)")

    if len(faces) > 0:
        x, y, w, h = faces[0]
        emb = embedding(img, x, y, w, h)
    else:
        print("  WARNING: no face detected in stored thumbnail - using full image")
        emb = embedding(img, 0, 0, img.shape[1], img.shape[0])

    for e in enrolled:
        score = cosine(emb, e['embedding'])
        match = "MATCH" if score >= 0.70 else ("CLOSE" if score >= 0.55 else "no match")
        print(f"  vs {e['name']:20s}: cosine={score:.4f}  -> {match}")
    print()

print("=== THRESHOLD ANALYSIS ===")
print("Current threshold: 0.70")
print("Tip: if all scores are below 0.70, lower the threshold in api_server.py")
