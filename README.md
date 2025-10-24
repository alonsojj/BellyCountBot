<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <a href="https://github.com/alonsojj/BellyCountBot">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Belly Count Bot</h3>

  <p align="center">
    AI-powered WhatsApp bot for automate customer service focused on accounting firms
    <br />
    <a href="https://github.com/alonsojj/BellyCountBot"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/alonsojj/BellyCountBot/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/alonsojj/BellyCountBot/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#environment-variables">Environment Variables</a></li>
    <li><a href="#api-documentation">API Documentation</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

[![Belly Count Bot Screenshot][product-screenshot]](https://github.com/alonsojj/BellyCountBot)

**Belly Count Bot** is an intelligent WhatsApp assistant...



- 🤖 **AI-Powered Conversations** - Natural language processing via Meta's Llama models through Groq
- 📧 **Email Reports** - Automated monthly/weekly financial reports sent to your inbox
- 💾 **Secure Database** - All data stored securely in PostgreSQL
- 📱 **WhatsApp Native** - Works seamlessly through Evolution API integration

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![Python][Python-badge]][Python-url]
* [![PostgreSQL][PostgreSQL-badge]][PostgreSQL-url]
* [![Groq][Groq-badge]][Groq-url]
* [![Docker][Docker-badge]][Docker-url]
* [![WhatsApp][WhatsApp-badge]][WhatsApp-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

Follow these instructions to set up Belly Count Bot locally.

### Prerequisites

Ensure you have the following installed:

1. **UV** - Fast Python package manager
   
   **Windows (PowerShell):**
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   
   **Linux/MacOS:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   
   **Via pipx:**
   ```bash
   pipx install uv
   ```

2. **Docker & Docker Compose**
   - [Install Docker](https://docs.docker.com/engine/install/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

3. **Groq API Key**
   - Sign up at [Groq Console](https://console.groq.com/)
   - Generate your API key

4. **Evolution API Instance**
   - Deploy Evolution API or use an existing instance
   - [Evolution API Documentation](https://doc.evolution-api.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/alonsojj/BellyCountBot.git
   cd BellyCountBot
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your credentials:
   ```env
   # Groq API (Meta AI)
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=llama-3.1-70b-versatile
   GROQ_TEMPERATURE=0.7
   
   # PostgreSQL Database
   POSTGRES_USER=bellycountbot
   POSTGRES_PASSWORD=your_secure_password_here
   POSTGRES_DB=bellycountbot_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
   
   # Evolution API (WhatsApp)
   EVOLUTION_API_URL=http://localhost:8080
   EVOLUTION_API_KEY=your_evolution_api_key
   EVOLUTION_INSTANCE_NAME=bellycountbot
   EVOLUTION_WEBHOOK_URL=http://your-server.com/webhook
   
   # Email Configuration (SMTP)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_FROM=your_email@gmail.com
   EMAIL_FROM_NAME=Belly Count Bot
   
   # FastAPI Settings
   API_HOST=0.0.0.0
   API_PORT=8000
   API_RELOAD=true
   DEBUG=false
   SECRET_KEY=your_secret_key_here_generate_with_openssl
   ```

4. **Start PostgreSQL and Evolution API containers**
   ```bash
   docker-compose up -d
   ```

5. **Start the FastAPI server**
   ```bash
   uvx fastapi app/main.py
   ```

6. **Configure WhatsApp connection**
   - Access Evolution API dashboard (usually at `http://localhost:8080`)
   - Scan QR code to connect your WhatsApp number
   - Configure webhook to point to your FastAPI endpoint

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### Starting a Conversation

Once configured, simply message your WhatsApp bot:

```

```

### Main Commands



Visit `http://localhost:8000/docs` for interactive API documentation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Project Structure

```
BellyCountBot/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration and environment variables
│   ├── database.py                  # PostgreSQL connection and session
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user_database.py
│   │   └── webhook.py
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── groq_service.py         # Groq/Meta AI integration
│   │   ├── whatsapp_service.py     # Evolution API integration
│   │   └── email_service.py        # Email sending functionality
│   │
│   ├── routers/                     # FastAPI route handlers
│   │   ├── __init__.py
│   │   └── webhook.py              # WhatsApp webhook endpoint
│   │
│   │
│   └── utils/                       # Helper functions
│       ├── __init__.py
│       ├── parsers.py              # Natural language parsing
│       ├── formatters.py           # Response formatting
│       └── validators.py           # Input validation
│
├── tests/                           # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
│
├── docker-compose.yml               # Docker services configuration
├── Dockerfile                       # Application container
├── pyproject.toml                   # UV/Python project config
├── .env.example                     # Environment variables template
├── .gitignore
├── LICENSE.txt
└── README.md
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for Meta AI | ✅ | - |
| `GROQ_MODEL` | Llama model to use | ✅ | - |
| `POSTGRES_USER` | PostgreSQL username | ✅ | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | ✅ | - |
| `POSTGRES_DB` | Database name | ✅ | `bellycountbot_db` |
| `POSTGRES_HOST` | Database host | ✅ | `localhost` |
| `POSTGRES_PORT` | Database port | ✅ | `5432` |
| `EVOLUTION_API_URL` | Evolution API base URL | ✅ | - |
| `EVOLUTION_API_KEY` | Evolution API authentication key | ✅ | - |
| `EVOLUTION_INSTANCE_NAME` | WhatsApp instance name | ✅ | - |
| `SMTP_HOST` | SMTP server host | ✅ | - |
| `SMTP_PORT` | SMTP server port | ✅ | `587` |
| `SMTP_USER` | SMTP username | ✅ | - |
| `SMTP_PASSWORD` | SMTP password | ✅ | - |
| `EMAIL_FROM` | Sender email address | ✅ | - |
| `API_PORT` | FastAPI port | ❌ | `8000` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints

#### Transactions
- `POST /api/v1/transactions` - Create new transaction
- `GET /api/v1/transactions` - List all transactions
- `GET /api/v1/transactions/{id}` - Get specific transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction

#### Reports
- `GET /api/v1/reports/monthly` - Generate monthly report
- `GET /api/v1/reports/yearly` - Generate yearly report
- `GET /api/v1/reports/category` - Report by category
- `POST /api/v1/reports/export` - Export to Excel/PDF

#### Webhook
- `POST /webhook/whatsapp` - Evolution API webhook endpoint

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- [x] Core WhatsApp bot functionality
- [ ] Groq/Meta AI integration for natural language
- [ ] Basic expense and income tracking
- [ ] PostgreSQL database setup
- [ ] Email notification system

See the [open issues](https://github.com/alonsojj/BellyCountBot/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
uv sync --all-groups

# Run tests
pytest

# Format code
ruff format app/

# Lint code
ruff lint app/
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top Contributors

<a href="https://github.com/alonsojj/BellyCountBot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=alonsojj/BellyCountBot" alt="contrib.rocks image" />
</a>

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - your_email@email.com

Project Link: [https://github.com/alonsojj/BellyCountBot](https://github.com/alonsojj/BellyCountBot)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

* [Evolution API](https://github.com/EvolutionAPI/evolution-api) - Open source WhatsApp API
* [Groq](https://groq.com/) - Lightning-fast LLM inference
* [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
* [UV](https://github.com/astral-sh/uv) - Extremely fast Python package manager
* [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
* [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
* [Pydantic](https://docs.pydantic.dev/) - Data validation library

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/alonsojj/BellyCountBot.svg?style=for-the-badge
[contributors-url]: https://github.com/alonsojj/BellyCountBot/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/alonsojj/BellyCountBot.svg?style=for-the-badge
[forks-url]: https://github.com/alonsojj/BellyCountBot/network/members
[stars-shield]: https://img.shields.io/github/stars/alonsojj/BellyCountBot.svg?style=for-the-badge
[stars-url]: https://github.com/alonsojj/BellyCountBot/stargazers
[issues-shield]: https://img.shields.io/github/issues/alonsojj/BellyCountBot.svg?style=for-the-badge
[issues-url]: https://github.com/alonsojj/BellyCountBot/issues
[license-shield]: https://img.shields.io/github/license/alonsojj/BellyCountBot.svg?style=for-the-badge
[license-url]: https://github.com/alonsojj/BellyCountBot/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/your_linkedin

[product-screenshot]: images/screenshot.png

[FastAPI-badge]: https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white&style=for-the-badge
[FastAPI-url]: https://fastapi.tiangolo.com/
[Python-badge]: https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge
[Python-url]: https://www.python.org/
[PostgreSQL-badge]: https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white&style=for-the-badge
[PostgreSQL-url]: https://www.postgresql.org/
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge
[Docker-url]: https://www.docker.com/
[Groq-badge]: https://img.shields.io/badge/Groq-000000?logo=&logoColor=white&style=for-the-badge
[Groq-url]: https://groq.com/
[WhatsApp-badge]: https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white&style=for-the-badge
[WhatsApp-url]: https://www.whatsapp.com/
