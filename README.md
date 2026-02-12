# 🤖 AI Virtual Assistant

Enterprise-grade AI Virtual Assistant with phone, email, and WhatsApp integration. Not just a chatbot—a fully autonomous assistant that can handle real-world business operations.

## ✨ Features

### MVP Phase 1 (Current)
- ☎️ **Phone Call Handling**: Receive and make calls via Twilio
- 🗣️ **Voice Cloning**: Clone voices using ElevenLabs for natural conversations
- 🎤 **Speech-to-Text**: Real-time transcription with OpenAI Whisper
- 🔊 **Text-to-Speech**: High-quality voice synthesis
- 🤖 **AI Conversations**: Intelligent responses powered by GPT-4 and LangChain
- 📊 **Call Logging**: Complete call history with transcriptions
- 🎯 **Web Dashboard**: Monitor and manage calls

### Future Phases
- 📧 Email automation (Gmail API)
- 💬 WhatsApp integration
- 📅 Calendar management (Google Calendar)
- 🔍 Information search and delivery
- 📈 Analytics and reporting

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              External Interfaces                │
│  [Phone] [Email] [WhatsApp] [Web Dashboard]    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            FastAPI Web Server                   │
│  /webhooks/twilio    /webhooks/whatsapp        │
│  /api/v1/*          /health                     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         LangChain Agent Orchestrator            │
│  ┌─────────────┐  ┌─────────────┐             │
│  │   Router    │  │  Context    │             │
│  │   Agent     │  │  Manager    │             │
│  └─────────────┘  └─────────────┘             │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Integration Services                   │
│  [Twilio] [ElevenLabs] [Whisper] [OpenAI]      │
│  [Gmail]  [WhatsApp]   [SerpAPI] [Calendar]    │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Poetry
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### 1. Clone Repository

```bash
git clone <repository-url>
cd AI-virtual-assistant
```

### 2. Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER
# - ELEVENLABS_API_KEY
nano .env
```

### 4. Start Services with Docker

```bash
# Start PostgreSQL, Redis, and the application
docker-compose up -d

# View logs
docker-compose logs -f api
```

### 5. Run Database Migrations

```bash
# Create initial migration
poetry run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
poetry run alembic upgrade head
```

### 6. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Development

### Local Development (Without Docker)

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run development server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Formatting

```bash
# Format code with Black
poetry run black src tests

# Sort imports with isort
poetry run isort src tests

# Lint with flake8
poetry run flake8 src tests
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_services/test_openai_service.py

# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration
```

## 🔧 Configuration

### Environment Variables

See [.env.example](.env.example) for all available configuration options.

Key variables:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `TWILIO_ACCOUNT_SID`: Twilio account identifier
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number
- `ELEVENLABS_API_KEY`: ElevenLabs API key for voice cloning
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Twilio Webhook Setup

For local development with Twilio:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update .env:
TWILIO_WEBHOOK_URL=https://abc123.ngrok.io/webhooks/twilio

# Configure Twilio webhook:
# Go to Twilio Console → Phone Numbers → Your Number
# Set Voice webhook to: https://abc123.ngrok.io/webhooks/twilio/voice
```

## 🎯 Usage

### Creating a Voice Clone

```bash
# Coming soon: Voice cloning script
poetry run python scripts/create_voice_clone.py \
  --name "John Doe" \
  --samples "./audio_samples/*.mp3"
```

### Making a Test Call

```bash
# Coming soon: Test call script
poetry run python scripts/test_call.py --number "+1234567890"
```

## 📊 API Endpoints

### Webhooks
- `POST /webhooks/twilio/voice` - Twilio incoming call webhook
- `POST /webhooks/twilio/status` - Call status updates
- `POST /webhooks/twilio/recording` - Recording callback

### API v1
- `GET /api/v1/calls` - List calls
- `GET /api/v1/calls/{id}` - Get call details
- `POST /api/v1/calls/outbound` - Make outbound call
- `GET /api/v1/voices` - List voice profiles
- `POST /api/v1/voices/clone` - Create voice clone
- `GET /health` - Health check

See [API Documentation](http://localhost:8000/docs) for full details.

## 🐳 Docker

### Build Custom Image

```bash
docker build -t ai-virtual-assistant:latest .
```

### Run Specific Services

```bash
# Run only database
docker-compose up -d postgres

# Run only API
docker-compose up -d api

# Run only Celery worker
docker-compose up -d celery_worker
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
```

## 🗄️ Database

### Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one version
poetry run alembic downgrade -1

# Show migration history
poetry run alembic history

# Show current version
poetry run alembic current
```

### Direct Database Access

```bash
# Connect to PostgreSQL (when running in Docker)
docker-compose exec postgres psql -U postgres -d ai_assistant

# Run SQL query
docker-compose exec postgres psql -U postgres -d ai_assistant -c "SELECT * FROM calls;"
```

## 📈 Monitoring

### Health Checks

```bash
# Check overall health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "database": "connected"}
```

### Logs

Structured logs are output in JSON format (production) or pretty-printed (development).

Example log entry:
```json
{
  "event": "Call received",
  "app": "AI Virtual Assistant",
  "environment": "development",
  "level": "info",
  "timestamp": "2024-02-12T10:30:00.000Z",
  "call_sid": "CAxxxxxxxxxxxxx",
  "from_number": "+1234567890"
}
```

## 🧪 Testing Strategy

- **Unit Tests**: Test individual services and utilities
- **Integration Tests**: Test API endpoints and database operations
- **End-to-End Tests**: Test complete call flows

## 🔒 Security

- Webhook signature verification (Twilio, WhatsApp)
- API key authentication
- Rate limiting
- Sensitive data redaction in logs
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)

## 📦 Project Structure

See [Implementation Plan](/home/houseph/.claude/plans/gentle-napping-blossom.md) for detailed project structure.

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `poetry run pytest`
4. Format code: `poetry run black src tests`
5. Commit with pre-commit hooks
6. Create pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **FastAPI**: Modern web framework
- **LangChain**: AI agent orchestration
- **OpenAI**: GPT-4 language model and Whisper STT
- **Twilio**: Phone infrastructure
- **ElevenLabs**: Voice cloning and TTS
- **PostgreSQL**: Reliable database
- **Redis**: Fast caching

## 📞 Support

For issues and questions:
- GitHub Issues: [Link]
- Email: [Support Email]
- Documentation: [Link]

---

**Status**: 🚧 MVP Phase 1 - In Development

**Version**: 0.1.0

**Last Updated**: 2026-02-12
