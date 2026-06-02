# Deployment Guide — AI Vision Face Recognition & Attendance System

Step-by-step instructions to install and run this system on another laptop
(Windows, macOS, or Linux). Commands below are written for **Windows PowerShell**;
equivalents for macOS/Linux are noted where they differ.

---

## 1. Architecture (what you are deploying)

| Component | Tech | Port | Notes |
|-----------|------|------|-------|
| **Backend API** | Python · FastAPI · OpenCV (YuNet + SFace DNN) | `8000` | Face detection, recognition, attendance |
| **Frontend Web** | Next.js (React) | `3000` | Live detection, register, logs, dashboard |
| **Database** | SQLite — `face_recognition.db` (repo root) | — | Employees, embeddings, logs, **and login** |
| **DNN models** | `models/*.onnx` (YuNet + SFace) | — | ~38 MB, downloaded separately |

The frontend (browser) calls the backend directly at `http://localhost:8000`,
so **both must be running at the same time**.

---

## 2. Prerequisites — software to install

Install these on the new laptop first:

1. **Python 3.10 – 3.14** — https://www.python.org/downloads/
   - During install, tick **“Add Python to PATH”**.
   - Verify: `python --version`
2. **Node.js 20 LTS or newer** — https://nodejs.org/
   - Verify: `node --version` and `npm --version`
3. **Git** (to clone the repo) — https://git-scm.com/
   - Verify: `git --version`
4. **Internet connection** — needed once, to download Python packages, npm
   packages, and the DNN model files. (Offline option in §4.)

> A working camera is required for live detection in the browser.

---

## 3. Get the code

```powershell
git clone <your-repo-url> face-detection-project
cd face-detection-project
git checkout dibya_chnage      # or the branch you deploy from
```

(Or copy the project folder to the new laptop — but **do not** copy `.venv`,
`web/node_modules`, or `web/.next`; those are machine-specific and get rebuilt.)

---

## 4. Backend (Python API) setup

From the **project root**:

```powershell
# 4a. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux:  source .venv/bin/activate

# 4b. Install backend dependencies (minimal, API-only)
pip install -r backend\requirements.txt

# 4c. Download the DNN face models (~38 MB, one-time, needs internet)
python backend\download_models.py
```

**Offline alternative for 4c:** copy the `models\` folder
(`face_detection_yunet_2023mar.onnx` + `face_recognition_sface_2021dec.onnx`)
from a machine that already has them into the project root. Without the models,
the API still starts but falls back to a much less accurate Haar detector.

---

## 5. Database — ships with the code ✅

`face_recognition.db` is committed in the repo, so the new laptop **already has**:

- all enrolled employees and their face embeddings,
- detection/attendance history,
- the admin login (default **`admin` / `Admin@123`**).

You don’t need to do anything. If the file is ever missing, the backend
auto-creates an empty database on first start (you’d then re-register employees
and log in with the default credentials above).

---

## 6. Frontend (web) setup

```powershell
cd web

# 6a. Install Node dependencies (rebuilds the native better-sqlite3 module)
npm install

# 6b. Point the web app at the backend (creates web\.env.local)
'NEXT_PUBLIC_API_URL=http://localhost:8000' | Out-File -Encoding utf8 .env.local

cd ..
```

> `.env.local` is intentionally **not** committed, so create it on each machine.

---

## 7. Run the system

Open **two terminals** in the project root.

**Terminal 1 — Backend:**
```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'face_detection_system'); from backend.api_server import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```
Wait for: `Detection pipeline: DNN(YuNet+SFace)=True`.

**Terminal 2 — Frontend:**
```powershell
cd web
npm run dev
```

**Windows one-click alternative:** double-click `START_SYSTEM.bat` in the project
root (starts both servers and opens the browser).

---

## 8. Open and log in

1. Browse to **http://localhost:3000**
2. Log in:
   - Username: **`admin`**
   - Password: **`Admin@123`**
3. Go to **Live Detection** → **Start Detection** → allow camera access.
   Recognized faces show a **green box + name**; unknown faces show a **red box**.

---

## 9. Health check

```powershell
# Backend should return detector "YuNet (DNN)"
curl http://localhost:8000/health
# Frontend should return HTTP 200
curl -o NUL -w "%{http_code}" http://localhost:3000/login
```

---

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| **“Cannot connect to the backend …”** in the UI | Backend isn’t running. Start Terminal 1 (§7). Both servers must run together. |
| Backend logs `DNN(YuNet+SFace)=False` | Models missing — run `python backend\download_models.py` (§4c). |
| `npm install` fails on **better-sqlite3** | Install Node 20+ and, on Windows, the “Desktop development with C++” build tools; then `npm install` again. |
| Port `8000` or `3000` already in use | Stop the other process, or change the port (backend: edit the `uvicorn.run(... port=)`; frontend: `npm run dev -- -p 3001` and update `.env.local`). |
| Camera not detected | Use `http://localhost` (browsers block camera on plain `http://<ip>`); grant the browser camera permission. |
| Login fails | Use `admin` / `Admin@123`. If you changed it, use the new password; resetting means editing `admin_credentials` in `face_recognition.db`. |
| Your face shows as **Unknown** | Re-register via the **Register** page (captures 5 aligned samples for a stronger template). |

---

## 11. Security notes

- `face_recognition.db` contains the **admin password** and **face embeddings
  (biometric data)**. Treat the repo as private. Change the default password
  after first login (Settings / change-password), and re-commit the DB if you
  want the new password to ship.
- The backend CORS is open (`*`) and binds `0.0.0.0` for LAN testing. For a real
  deployment, restrict CORS and bind to `127.0.0.1`.

---

## 12. What ships vs. what is rebuilt per machine

| Ships in git | Rebuilt / created on each machine |
|--------------|-----------------------------------|
| Source code (backend, web) | `.venv\` (Python venv) |
| `face_recognition.db` (data + login) | `web\node_modules\` (`npm install`) |
| `backend\requirements.txt`, `requirements.txt` | `web\.next\` (build cache) |
| `backend\download_models.py` | `models\*.onnx` (download or copy) |
| `START_SYSTEM.bat` | `web\.env.local` (one line, §6b) |
