# Cipher Messenger

A real-time messaging platform with AI-powered features built with FastAPI and Python.

## Features

- **Real-time messaging** via WebSocket with Redis pub/sub
- **Voice-to-text** transcription using Whisper
- **Auto-translation** across 100+ language pairs via Helsinki-NLP
- **Chat summarization** of long conversations using BART (Map-Reduce pipeline)
- **JWT authentication** with access/refresh token rotation
- **Group and private chats**

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis

**ML Service:** Whisper, Helsinki-NLP, BART (HuggingFace Transformers), PyTorch

**Infrastructure:** Docker, Docker Compose, nginx

## Architecture
```
browser
  │
nginx (port 80)
  │
  ├── Backend FastAPI (port 8000)
  │     ├── PostgreSQL
  │     └── Redis (WebSocket pub/sub)
  │
  └── ML Service (port 8001)
        ├── Whisper (transcription)
        ├── Helsinki-NLP (translation)
        └── BART (summarization)
```

## Getting Started

**Requirements:** Docker, Docker Compose

**1. Clone the repository**
```bash
git clone https://github.com/ssoltybekov/messenger-app.git
cd messenger-app
```

**2. Run all services**
```bash
docker-compose up --build
```

**3. Apply database schema**
```bash
docker exec -i messenger_db psql -U sanzhar -d messenger_db < backend/schema.sql
```

**4. Open in browser**
```
http://localhost
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| GET | `/chats/` | Get user chats |
| POST | `/chats/` | Create new chat |
| GET | `/messages/{chat_id}` | Get chat messages |
| WS | `/ws` | WebSocket connection |

## ML Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/audio/transcribe` | Voice to text (Whisper) |
| POST | `/translate/` | Auto-translate text |
| POST | `/summarize/` | Summarize chat messages |

## Environment Variables

Create a `.env` file in `backend/`:
```
DATABASE_URL=postgresql://user:password@db:5432/messenger_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your_secret_key
```

## Author

Sanzhar Soltybekov — [github.com/ssoltybekov](https://github.com/ssoltybekov)