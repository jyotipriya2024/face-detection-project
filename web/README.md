# AI Vision Face Recognition System

A modern face recognition system built with Next.js (frontend) and FastAPI (backend), featuring real-time face detection, emotion recognition, and person registration.

## Project Structure

```
face-detection-project/
├── backend/              # FastAPI backend server
│   ├── main.py          # Main FastAPI application
│   ├── api_server.py     # API server with auth
│   └── debug_search.py  # Database debugging tools
├── web/                 # Next.js frontend application
│   ├── src/             # React components and pages
│   ├── public/          # Static assets
│   └── package.json     # Frontend dependencies
├── database.py          # SQLite database operations
├── face_engine.py       # Face detection & recognition engine
├── emotion_detector.py  # Emotion detection module
└── face_recognition.db  # SQLite database (auto-created)
```

## Prerequisites

Before installing, ensure you have the following installed:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js) or yarn/pnpm/bun
- **Git** - [Download here](https://git-scm.com/downloads)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd face-detection-project
```

### 2. Backend Setup (FastAPI)

Navigate to the project root and install Python dependencies:

```bash
# Create a virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart
```

The backend uses the following key Python packages:
- `opencv-python` - Computer vision operations
- `mediapipe` - Face detection
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `numpy` - Numerical operations
- `scikit-learn` - Machine learning utilities

### 3. Frontend Setup (Next.js)

Navigate to the web directory and install Node.js dependencies:

```bash
cd web

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

The frontend uses the following key packages:
- `next` - React framework
- `react` - UI library
- `framer-motion` - Animations
- `lucide-react` - Icons
- `recharts` - Data visualization
- `@radix-ui/*` - UI components

## Running the Application

### Option 1: Run Both Services (Recommended)

**Terminal 1 - Backend:**
```bash
# From project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# From web directory
cd web
npm run dev
```

### Option 2: Run Backend Only

```bash
# From project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the API documentation at: http://localhost:8000/docs

### Option 3: Run Frontend Only

```bash
# From web directory
cd web
npm run dev
```

Access the frontend at: http://localhost:3000

## Access Points

Once both services are running:

- **Frontend Application:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation (Swagger):** http://localhost:8000/docs
- **API Documentation (ReDoc):** http://localhost:8000/redoc

## Environment Configuration

### Backend Environment Variables (Optional)

Create a `.env` file in the project root:

```env
# Database
DB_PATH=./face_recognition.db

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### Frontend Environment Variables

The frontend uses `.env.local` for configuration. Create it in the `web/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Available API Endpoints

### Health Check
- `GET /health` - Check if backend is running

### Statistics
- `GET /api/stats` - Get system statistics (detections, persons, recognition rate)

### Person Management
- `GET /api/persons` - Get all registered persons
- `POST /api/register` - Register a new person
- `DELETE /api/persons/{person_id}` - Delete a person

### Face Detection
- `POST /api/detect` - Detect faces in an image
- `POST /api/search` - Search for faces in the database

### Logs
- `GET /api/logs?limit=100` - Get detection logs

## Database

The system uses SQLite database (`face_recognition.db`) which is automatically created on first run. It includes:

- `persons` - Registered persons with face embeddings
- `detection_logs` - Face detection history
- `attendance` - Attendance records
- `admin_credentials` - Admin authentication

## Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'cv2'`
```bash
pip install opencv-python
```

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install fastapi uvicorn
```

**Issue:** Port 8000 already in use
```bash
# Use a different port
python -m uvicorn backend.main:app --port 8001
```

### Frontend Issues

**Issue:** `Module not found: Can't resolve 'react'`
```bash
cd web
npm install
```

**Issue:** Port 3000 already in use
```bash
# Use a different port
npm run dev -- -p 3001
```

**Issue:** Build errors
```bash
# Clear Next.js cache and rebuild
cd web
rm -rf .next
npm run dev
```

### Camera Access Issues

If the frontend cannot access your camera:
1. Ensure you're using HTTPS or localhost
2. Check browser camera permissions
3. Try a different browser (Chrome/Firefox recommended)

## Development

### Backend Development

```bash
# Run with auto-reload
python -m uvicorn backend.main:app --reload

# Run specific API server
python -m uvicorn backend.api_server:app --reload
```

### Frontend Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Production Deployment

### Backend Deployment

For production, use a production ASGI server:

```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

Build the frontend for production:

```bash
cd web
npm run build
npm start
```

Deploy to platforms like:
- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**
- **Docker containers**

## Docker Deployment (Optional)

Create a `Dockerfile` for the backend and use Docker Compose to run both services.

## Support

For issues or questions:
- Check the API documentation at http://localhost:8000/docs
- Review the code comments in `backend/main.py` and `web/src/`
- Ensure all prerequisites are installed correctly

## License

This project is part of M.Tech CSE 2024-2026 research at GIFT Bhubaneswar.
