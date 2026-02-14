# Team2 - Wiki Article Management System

A full-stack wiki-style article management platform with version control, collaborative publishing workflows, AI-powered tagging/summarization, and semantic search capabilities.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Background Tasks](#background-tasks)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Docker Services](#docker-services)

---

## Overview

Team2 is a Django-based wiki application that allows users to:
- Create and manage articles with full version control
- Collaborate through a publish request workflow
- Vote on articles (upvote/downvote)
- Search articles using Elasticsearch semantic search
- Automatically generate summaries and tags using AI (Gemini)

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React SPA     │────▶│  Nginx Gateway  │────▶│  Django Core    │
│   (Vite)        │     │                 │     │  (REST API)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                        ┌───────────────────────────────┼───────────────────────────────┐
                        │                               │                               │
                        ▼                               ▼                               ▼
                ┌───────────────┐              ┌───────────────┐              ┌───────────────┐
                │    Redis      │              │ Elasticsearch │              │   Celery      │
                │   (Broker)    │              │   (Search)    │              │   (Workers)   │
                └───────────────┘              └───────────────┘              └───────────────┘
                                                                                      │
                                                                                      ▼
                                                                              ┌───────────────┐
                                                                              │  Gemini AI    │
                                                                              │  (Tags/Sum)   │
                                                                              └───────────────┘
```

---

## Features

### Article Management
- **Create Articles**: Users can create new articles with unique names
- **Version Control**: Each article supports multiple versions with full content history
- **Current Version**: Articles have a designated "current" published version

### Collaborative Publishing
- **Direct Publish**: Article creators can publish versions directly
- **Publish Requests**: Non-creators can request to publish their versions
- **Approval Workflow**: Creators can approve or reject publish requests

### Voting System
- **Upvote/Downvote**: Users can vote on articles (+1 or -1)
- **Score Tracking**: Articles maintain a cumulative score
- **Vote Modification**: Users can change their vote

### Search & Discovery
- **Semantic Search**: Elasticsearch-powered full-text search
- **Fuzzy Matching**: Handles typos and variations
- **Weighted Fields**: Tags and summaries are prioritized in search results
- **Top Rated**: Browse articles by score
- **Newest**: Browse recently updated articles
- **By Tag**: Discover top articles grouped by tag

### AI-Powered Features
- **Auto-Tagging**: Gemini AI suggests relevant tags from existing tags or creates new ones
- **Auto-Summarization**: Generates 3-6 sentence summaries in Farsi
- **Background Processing**: AI tasks run asynchronously via Celery

---

## Tech Stack

### Backend
- **Django** + **Django REST Framework** - Web framework & API
- **Celery** - Async task queue
- **Redis** - Message broker for Celery
- **Elasticsearch 8.12** - Search engine
- **SQLite** - Database (development)
- **Google Gemini AI** - Tagging and summarization

### Frontend
- **React 18** - UI framework
- **Vite 6** - Build tool
- **React Router 6** - Client-side routing
- **TailwindCSS 3** - Styling
- **Lucide React** - Icons
- **React Markdown** - Markdown rendering

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - API gateway / reverse proxy
- **Flower** - Celery monitoring dashboard

---

## Project Structure

```
team2/
├── frontend/                 # React SPA
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route pages
│   │   │   ├── HomePage.jsx
│   │   │   ├── SearchPage.jsx
│   │   │   ├── ArticlePage.jsx
│   │   │   ├── MyArticlePage.jsx
│   │   │   ├── NewArticlePage.jsx
│   │   │   ├── ManageArticlePage.jsx
│   │   │   ├── EditVersionPage.jsx
│   │   │   ├── PreviewVersionPage.jsx
│   │   │   ├── RequestPublishPage.jsx
│   │   │   ├── ReviewPublishPage.jsx
│   │   │   └── MyRequestsPage.jsx
│   │   ├── api.js            # API client
│   │   ├── App.jsx           # Main app with routes
│   │   └── main.jsx          # Entry point
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── tasks/                    # Celery tasks
│   ├── tasks.py              # AI tasks (tagging, summarization)
│   └── indexing.py           # Elasticsearch indexing
├── migrations/               # Django migrations
├── static/team2/             # Static files
├── templates/team2/          # Django templates
├── models.py                 # Database models
├── views.py                  # API views
├── urls.py                   # URL routing
├── serializers.py            # DRF serializers
├── authentication.py         # JWT authentication
├── admin.py                  # Django admin config
├── docker-compose.yml        # Docker services
├── gateway.conf              # Nginx configuration
└── Dockerfile
```

---

## Data Models

### Tag
| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField (PK) | Tag name |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### Article
| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField (PK) | Unique article name |
| `creator_id` | UUID | User who created the article |
| `current_version` | FK → Version | Currently published version |
| `score` | Integer | Cumulative vote score |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### Version
| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField (PK) | Unique version name |
| `article` | FK → Article | Parent article |
| `content` | TextField | Markdown content |
| `summary` | TextField | AI-generated summary |
| `editor_id` | UUID | User who created this version |
| `tags` | M2M → Tag | Associated tags |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### PublishRequest
| Field | Type | Description |
|-------|------|-------------|
| `id` | Auto (PK) | Request ID |
| `version` | FK → Version | Version to publish |
| `article` | FK → Article | Target article |
| `requester_id` | UUID | User requesting publish |
| `status` | Choice | `pending`, `approved`, `rejected` |
| `created_at` | DateTime | Creation timestamp |

### Vote
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | UUID | Voting user |
| `article` | FK → Article | Voted article |
| `value` | SmallInt | +1 (upvote) or -1 (downvote) |

---

## API Endpoints

### Articles

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/articles/create/` | ✅ | Create a new article |
| `GET` | `/api/articles/<name>/` | ❌ | Get article by name |
| `GET` | `/api/articles/mine/` | ✅ | List user's articles |
| `GET` | `/api/articles/search/?q=` | ❌ | Semantic search |
| `GET` | `/api/articles/newest/` | ❌ | 10 newest articles |
| `GET` | `/api/articles/top-rated/` | ❌ | 10 top-rated articles |
| `GET` | `/api/articles/top-by-tag/` | ❌ | Top articles by tag |

### Versions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/versions/create/` | ✅ | Create version from existing |
| `POST` | `/api/versions/create-empty/` | ✅ | Create empty version |
| `GET` | `/api/versions/<name>/` | ✅ | Get version details |
| `PATCH` | `/api/versions/<name>/update/` | ✅ | Update version content |
| `POST` | `/api/versions/<name>/publish/` | ✅ | Publish version (creator only) |

### Voting

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/vote/` | ✅ | Vote on article (+1/-1) |

### Publish Requests

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/publish-requests/create/` | ✅ | Request to publish a version |
| `GET` | `/api/publish-requests/article/<name>/` | ✅ | List pending requests (creator) |
| `GET` | `/api/publish-requests/mine/<name>/` | ✅ | List user's requests |
| `POST` | `/api/publish-requests/<id>/approve/` | ✅ | Approve request (creator) |
| `POST` | `/api/publish-requests/<id>/reject/` | ✅ | Reject request (creator) |

### Wiki Integration

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/wiki/?content=` | ❌ | Get wiki content for a topic |

---

## Background Tasks

### Celery Tasks

| Task | Description | Trigger |
|------|-------------|---------|
| `tag_article` | Uses Gemini AI to suggest/create tags | On publish |
| `summarize_article` | Generates Farsi summary with Gemini | On publish |
| `index_article_version` | Indexes article in Elasticsearch | After tagging/summarization |
| `index_all_articles` | Bulk re-index all articles | Manual |

### Task Flow on Publish

```
publish_version() 
    │
    ├──▶ tag_article.s(article_name)  ─────┐
    │                                       │
    └──▶ summarize_article.s(article_name) ─┼──▶ index_article_version.s(version_name)
                                            │
                                   (chord callback)
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker

1. **Create the external network** (if not exists):
   ```bash
   docker network create app404_net
   ```

2. **Set environment variables**:
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your configuration
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: `http://localhost:${TEAM_PORT}`
   - Flower (Celery monitor): `http://localhost:5555`
   - Elasticsearch: `http://localhost:9200`

### Local Frontend Development

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TEAM_PORT` | Port for the gateway | `8002` |
| `TEAM2_FRONT_URL` | Frontend URL for redirects | `http://localhost:8002` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `ELASTICSEARCH_URL` | Elasticsearch URL | `http://elasticsearch:9200` |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend | `redis://redis:6379/0` |

---

## Docker Services

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| `gateway` | nginx:alpine | `${TEAM_PORT}:80` | Reverse proxy |
| `elasticsearch` | elasticsearch:8.12.1 | `9200:9200` | Search engine |
| `redis` | redis:7-alpine | - | Message broker |
| `team2-celery` | (built) | - | Celery worker |
| `team2-flower` | (built) | `5555:5555` | Celery monitoring |
| `team2-frontend` | (built) | - | React SPA |

---

## Frontend Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | HomePage | Landing page with top/newest articles |
| `/search` | SearchPage | Semantic article search |
| `/my-articles` | MyArticlePage | User's created articles |
| `/articles/new` | NewArticlePage | Create new article |
| `/articles/:name` | ArticlePage | View article |
| `/articles/:name/manage` | ManageArticlePage | Manage article versions |
| `/articles/:name/requests` | RequestPublishPage | View publish requests (creator) |
| `/articles/:name/my-requests` | MyRequestsPage | User's publish requests |
| `/versions/:name/edit` | EditVersionPage | Edit version content |
| `/versions/:name/preview` | PreviewVersionPage | Preview version |

---

## License

This project is part of the Software Engineering 1404-01 course (Group 2).
