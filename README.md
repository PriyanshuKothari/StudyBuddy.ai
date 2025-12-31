---
title: StudyBuddy.ai
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🎓 StudyBuddy.ai

> AI-powered study assistant that helps students learn through intelligent conversations with their own study materials.

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](./backend)
[![Frontend](https://img.shields.io/badge/Frontend-Coming%20Soon-blue)](./frontend)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 Live Demo

**Backend API:** https://studybuddy-ai-9hu3.onrender.com/docs  
**Frontend:** (https://study-buddy-ai-liard.vercel.app/)

---

## 📁 Project Structure

```
StudyBuddy.ai/
├── studybuddy/          # FastAPI + RAG Pipeline
│   ├── app/          # Application code
│   ├── Dockerfile    # Container config
│   └── README.md     # Backend docs
│
├── studybuddy-frontend/         # React UI (Coming Soon)
│   └── ...
│
└── README.md         # This file
```

---

## ✨ Features

### 📄 **Document Intelligence**
- Upload PDFs (syllabus, notes, textbooks)
- Automatic text extraction and semantic chunking
- Vector embeddings for intelligent search

### 🤖 **AI-Powered Q&A**
- Ask questions in natural language
- Get accurate answers with source citations
- Retrieval Augmented Generation (RAG)

### 💬 **Smart Conversations**
- Multi-turn dialogue with context awareness
- Follow-up questions work naturally
- Session-based chat history

### 🎯 **Coming Soon**
- Previous Year Question Paper Analysis
- Mock question generation
- Topic frequency detection
- Priority study recommendations

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **LLM:** Groq (Llama 3.1 8B)
- **Vector DB:** ChromaDB
- **Embeddings:** HuggingFace Transformers
- **Orchestration:** LangChain
- **PDF Processing:** PyPDF

### Frontend (Planned)
- **Framework:** React + TypeScript
- **UI Library:** Tailwind CSS + shadcn/ui
- **State Management:** Zustand
- **API Client:** Axios

---

## 🏃 Quick Start

### Prerequisites
- Python 3.12+
- Groq API key ([Get one](https://console.groq.com))
- Docker (optional)

### Backend Setup

```bash
cd studybuddy
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
GROQ_API_KEY=your_key_here
HF_TOKEN=your_hf_token_here
```

Run server:
```bash
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000/docs`

### Docker Deployment

```bash
cd studybuddy
docker build -t studybuddy .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e HF_TOKEN=your_token \
  studybuddy
```

---

## 📖 API Documentation

**Interactive docs:** `/docs` (Swagger UI)

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload/pdf` | Upload study materials |
| POST | `/api/v1/rag/chat` | Ask questions about docs |
| GET | `/api/v1/rag/history/{id}` | View chat history |
| DELETE | `/api/v1/rag/history/{id}` | Clear history |
| POST | `/api/v1/chat` | General AI chat |

---

## 🎯 Use Cases

- **Students:** Interactive learning with textbooks
- **Researchers:** Query papers instantly
- **Professionals:** Understand technical docs
- **Exam Prep:** Analyze PYQs and generate mocks

---

## 🗺️ Roadmap

### Phase 1: Core RAG ✅
- [x] PDF upload and processing
- [x] Vector embeddings and search
- [x] Multi-turn conversations
- [x] Source attribution

### Phase 2: Advanced Features 🚧
- [x] PYQ analysis and topic frequency
- [x] Mock question generation
- [x] Study priority recommendations
- [x] Streaming responses

### Phase 3: Full Stack 📅
- [x] React frontend with chat UI
- [x] User authentication
- [x] Multi-document support
- [x] Mobile app

---

## 🤝 Contributing

Contributions welcome! See individual README files in `studybuddy/` and `studybuddy-frontend/` folders.

---

## 📝 License

MIT License - Free to use for learning and projects

---

## 👨‍💻 Author

**Priyanshu Kothari**

🔗 [LinkedIn](https://www.linkedin.com/in/priyanshu-kothari-1044b32bb/) | [GitHub](https://github.com/PriyanshuKothari) 

---

⭐ **Star this repo if you find it useful!**

📧 Questions? Open an issue or reach out!

---

## 🙏 Acknowledgments

Built with: FastAPI, LangChain, Groq, ChromaDB, HuggingFace

Special thanks to the open-source community!
