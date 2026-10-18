# AutomyEm — AI-Powered Email Workflow Automation

<p align="center">
  <strong>Turn inbox overload into actionable intelligence.</strong>
  <br />
  An AI-powered email workflow system designed to simplify email management through intelligent analysis, automation, and asynchronous processing.
  <br /><br />
  <a href="https://automate-my-email.onrender.com/">
    <img src="https://img.shields.io/badge/API-Live-2ea44f?style=for-the-badge&logo=render&logoColor=white" alt="Live API" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/AI-Groq_LLM-F55036?style=for-the-badge" alt="Groq LLM" />
  <br />
  <img src="https://img.shields.io/badge/Redis-Job_Queue-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Gmail-API-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Gmail API" />
</p>

---

## ✦ Overview

Email is essential to modern work, but manually reviewing, prioritizing, and responding to messages can consume valuable time.

**AutomyEm** explores how AI and backend engineering can make this workflow more efficient.

It integrates with Gmail to synchronize emails, uses a large language model (LLM) to extract useful insights, and supports task-oriented workflows through a dedicated backend and persistent storage.

Rather than performing AI inference directly inside every request, AutomyEm uses a **Redis-backed background job queue** to separate email synchronization from AI analysis.

The result is a more modular approach to building AI-powered applications, with a focus on maintainability, asynchronous processing, and error handling.

## ✨ Features

| Capability | Description |
|---|---|
| 📬 Gmail integration | Connects to Google services through OAuth and synchronizes emails. |
| 🧠 AI-powered analysis | Generates summaries, classifies email categories, identifies priority, and suggests replies. |
| ⚡ Background processing | Uses Redis queues to process email analysis separately from the initial API request. |
| 🔐 Authentication | Supports user authentication and Google OAuth integration. |
| 🗄️ Persistent storage | Stores email records, analysis results, and tasks in PostgreSQL through SQLAlchemy. |
| 📝 Task workflows | Supports task-related operations associated with email management. |
| 🛡️ Failure handling | Handles failed jobs and AI provider errors through queue-based processing. |
| 🌐 REST API | Exposes backend functionality through FastAPI endpoints. |

## 🏗️ Architecture

AutomyEm separates email ingestion from AI analysis so that potentially time-consuming model requests can be processed independently.

```mermaid
flowchart TD
    A[User / Frontend] --> B[FastAPI Backend]
    B --> C[Authentication & OAuth]
    B --> D[Gmail API]
    D --> E[Email Synchronization]
    E --> F[(PostgreSQL)]
    E --> G[Redis Job Queue]
    G --> H[Background Worker]
    H --> I[Groq LLM]
    I --> H
    H --> J[Store Analysis Results]
    J --> F
    F --> K[Analysis & Task APIs]
    K --> A
```

### Processing flow

1. **Authenticate** — The user accesses the application and connects their Google account.
2. **Synchronize** — The backend retrieves email data from Gmail and persists email records.
3. **Enqueue** — Email analysis jobs are added to a Redis-backed queue.
4. **Process** — A background worker retrieves jobs and sends the relevant email content to the Groq model.
5. **Persist** — Successful analysis results are saved to PostgreSQL.
6. **Retrieve** — The frontend accesses stored email analysis and task information through the API.

> **Design principle:** Keep email ingestion and AI inference separate to improve modularity and make failure handling easier to manage.

## 🧠 AI capabilities

AutomyEm uses Groq-hosted LLM inference to analyze email content.

The analysis workflow can produce:

- **Summary:** A concise overview of the email.
- **Priority:** An indication of how urgently the email may need attention.
- **Category:** A classification of the email's purpose.
- **Action required:** An indication of whether the email calls for a follow-up or action.
- **Suggested reply:** A draft response to help the user respond more efficiently.

These outputs are stored for retrieval by the application.

*AI-generated content should be reviewed before being used for important communications.*

## ⚙️ Technology stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python | Application and processing logic |
| Backend | FastAPI | REST API and request handling |
| ORM | SQLAlchemy | Database models and operations |
| Database | PostgreSQL | Persistent application data |
| Queue / Cache | Redis | Background job queuing and processing state |
| AI inference | Groq API | LLM-powered email analysis |
| Email integration | Gmail API | Email synchronization |
| Authentication | Google OAuth and application authentication | User access and Google account authorization |
| Deployment | Render | Hosting the backend API |
| Redis hosting | Upstash Redis | Managed Redis infrastructure |

## ⚡ Why a background queue?

LLM calls can take time, fail temporarily, or encounter provider rate limits. Performing all processing synchronously inside an API request can make the application less responsive.

AutomyEm uses Redis to decouple job submission from job execution.

```mermaid
flowchart LR
    A[Email Saved] --> B[Job Enqueued]
    B --> C[Pending Queue]
    C --> D[Background Worker]
    D --> E{Analysis Result}
    E -->|Success| F[Save to Database]
    E -->|Failure| G[Retry Policy]
    G -->|Attempts Remaining| C
    G -->|Retries Exhausted| H[Failed Job Queue]
```

The worker maintains separate queues for pending, processing, and failed jobs.

The intended processing strategy includes:

- Moving jobs into a processing queue before analysis.
- Recovering stranded processing jobs when the worker restarts.
- Retrying eligible failures a limited number of times.
- Sending exhausted or explicitly non-retryable jobs to a failed queue.
- Persisting successful analysis results in the database.

This approach improves the structure of the processing workflow, although it does not by itself guarantee exactly-once processing or uninterrupted execution.

## 🛡️ Error handling and resilience

AI applications need to account for failures beyond ordinary Python exceptions.

AutomyEm addresses several important scenarios:

| Scenario | Handling strategy |
|---|---|
| Temporary processing failure | Apply the configured retry policy. |
| Groq token-per-minute limit exceeded | Treat HTTP 413 with `rate_limit_exceeded` as a non-retryable job failure in the current worker design. |
| Worker interruption | Recover jobs left in the processing queue when the worker restarts. |
| Invalid job data | Reject the invalid job and route it to failure handling. |
| API communication failure | Return or display an appropriate error where the request-response flow exposes it. |

**Important distinction:** A background job failure is not automatically an HTTP error for the original frontend request. The application needs a way to expose job status or failure details through an API endpoint if the frontend is to display the result accurately.

Provider rate limits can also change with account tier and usage. Queueing helps manage processing, but it does not eliminate rate limits.

## 📂 Project structure

The following is a logical overview of the key modules; exact paths may vary as the project evolves.

```text
AutomyEm/
├── app/
│   ├── api/
│   │   ├── email.py
│   │   ├── email_analysis.py
│   │   ├── oauth.py
│   │   ├── task.py
│   │   └── user.py
│   ├── core/
│   │   ├── config.py
│   │   └── redis_config.py
│   ├── database/
│   │   └── database.py
│   ├── models/
│   │   ├── email.py
│   │   ├── email_analysis.py
│   │   ├── task.py
│   │   └── user.py
│   ├── services/
│   │   ├── ai_service.py
│   │   └── queue_service.py
│   ├── workers/
│   │   └── email_worker.py
│   └── main.py
├── requirements.txt
├── .env.example
└── README.md
```

### Module responsibilities

- `app/api/` — API routes for email operations, analysis, OAuth, users, and tasks.
- `app/core/` — Application configuration and Redis client setup.
- `app/database/` — Database engine, session management, and SQLAlchemy base.
- `app/models/` — Persistent database models.
- `app/services/ai_service.py` — AI-powered email analysis.
- `app/services/queue_service.py` — Submission of email-analysis jobs.
- `app/workers/email_worker.py` — Background job processing and failure recovery.
- `app/main.py` — FastAPI application initialization, router registration, and worker lifecycle.

## 🚀 Getting started

### Prerequisites

Before running AutomyEm locally, prepare:

- Python 3.x compatible with the project's dependencies.
- A PostgreSQL database.
- A Redis instance, such as a local Redis server or Upstash Redis.
- A Groq API key.
- Google Cloud credentials with the required Gmail API enabled.
- A configured Google OAuth consent screen and authorized redirect URI.

### 1. Clone the repository

```bash
git clone https://github.com/mohits2005/Automate-My-Email.git
cd Automate-My-Email
```

### 2. Create a virtual environment

**Windows — PowerShell**

```powershell
python -m venv myEm
.\myEm\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv myEm
source myEm/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the location expected by your application configuration. Use `.env.example` as the reference if one is provided in the repository.

Typical configuration values include:

```dotenv
SECRET_KEY=replace_with_a_strong_random_secret
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your_groq_api_key
```

These names are illustrative. Use the exact environment variable names and database URL format expected by the current application code and deployment environment. For hosted Redis, use the connection URL and credentials supplied by your provider.

**Security:** Never commit `.env`, OAuth client secrets, access tokens, refresh tokens, or API keys to version control.

### 5. Configure Google OAuth

1. Create or select a project in Google Cloud Console.
2. Enable the Gmail API.
3. Configure the OAuth consent screen.
4. Create OAuth client credentials appropriate for your application.
5. Configure the authorized redirect URI to match the callback route in your backend.
6. Add the required credentials to your environment configuration.

The OAuth flow must use the correct callback URL for both local development and the deployed application.

### 6. Start the application

From the repository root, run:

```bash
uvicorn app.main:app --reload
```

Open the local API documentation at:

**http://127.0.0.1:8000/docs**

Use the interactive documentation to explore available endpoints and test supported operations.

The application starts its background worker through the FastAPI lifespan when configured accordingly. Avoid launching a second worker unintentionally when testing this integrated setup.

## ☁️ Deployment

AutomyEm's backend is deployed on Render and uses managed Redis infrastructure.

### Deployment checklist

1. Push the application code to the configured Git repository.
2. Create or update the Render web service.
3. Configure the build and start commands.
4. Set the required environment variables in the Render dashboard.
5. Configure the production database and Redis connection.
6. Update the Google OAuth redirect URI to the deployed callback URL.
7. Deploy and review startup logs.
8. Test API connectivity, email synchronization, queue processing, and database persistence.

### Operational considerations

- A Render free web service may sleep when idle, depending on the current platform policy. A worker running inside that service will not operate continuously while the service is suspended.
- A single-service deployment is suitable for experimentation, but sustained background processing may require a separately managed worker or an always-on deployment plan.
- If multiple worker processes or instances are introduced, job recovery and queue ownership must be designed to avoid re-queuing jobs that another worker is actively processing.

## 🔍 Testing and troubleshooting

### API health check

Open the deployed API root:

[https://automate-my-email.onrender.com/](https://automate-my-email.onrender.com/)

The root endpoint should return the application's configured status message when the service is available.

### Common issues

| Issue | What to check |
|---|---|
| API unavailable | Service status, deployment logs, URL configuration, and possible cold-start delay. |
| Redis connection error | Redis URL, credentials, TLS requirements, and network access. |
| Google OAuth error | Client ID, client secret, consent configuration, and redirect URI. |
| Groq HTTP 413 | Request token usage, email content length, and current provider limits. |
| Analysis remains pending | Worker startup, Redis queue contents, and database connectivity. |
| Analysis fails | Worker logs, provider response, retry policy, and failed-job queue. |
| Frontend displays a connection error | Distinguish a genuine network failure from an HTTP error or a background job failure. |

For AI requests that exceed the provider's token-per-minute limit, consider limiting or chunking the content before sending it to the model. Do not assume that every HTTP 413 response has the same cause; inspect the provider's error details.

## 🔐 Security considerations

AutomyEm integrates email and AI services, so protecting credentials and user data is essential.

- Store secrets in environment variables or a managed secret store.
- Keep OAuth tokens private and restrict access to authorized users.
- Never expose API keys in frontend code or public repositories.
- Validate and authorize access to user-specific email records.
- Avoid logging full email bodies, OAuth tokens, or sensitive personal data unnecessarily.
- Review AI-generated summaries and replies before relying on them for consequential decisions.

## 🗺️ Roadmap

Potential future improvements include:

- [ ] Expose explicit analysis-job status and failure details to the frontend.
- [ ] Add exponential backoff and provider-aware rate-limit handling.
- [ ] Add configurable email-content limits and token-aware chunking.
- [ ] Improve worker observability with structured logs and processing metrics.
- [ ] Add automated tests for queue recovery, retries, and failure handling.
- [ ] Introduce stronger job idempotency and concurrency controls.
- [ ] Add filtering, search, and richer email-management workflows.
- [ ] Improve deployment support for independent, continuously running workers.

## 💡 What this project demonstrates

AutomyEm is an exploration of practical backend engineering for AI-powered applications, including:

- REST API design and modular service architecture.
- OAuth integration with an external email provider.
- Relational database modeling and persistence.
- Redis-backed asynchronous job processing.
- LLM integration and structured analysis outputs.
- Error handling, retry policies, and recovery workflows.
- Deployment and configuration of a cloud-hosted application.

The central engineering challenge is not just calling an AI model — it is building the surrounding system that can process work, persist results, and handle failures in a predictable way.

## 👨‍💻 Author

**Mohit Sharma**

Software Engineer | Python · FastAPI · Backend Development · AI Integration

- GitHub: [mohits2005](https://github.com/mohits2005)
- Project repository: [Automate-My-Email](https://github.com/mohits2005/Automate-My-Email)
- Live API: [automate-my-email.onrender.com](https://automate-my-email.onrender.com/)

## 📄 License

Add the appropriate license for this repository if one has been selected. Until then, refer to the license file in the repository, if present, before redistributing or reusing the code.

---

<p align="center">
  <strong>Built to make everyday email workflows more intelligent.</strong>
  <br />
  <em>Learning, building, and improving — one system at a time.</em>
</p>
