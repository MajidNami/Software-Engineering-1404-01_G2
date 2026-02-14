# Wiki Service  
**Team: NullTerminated**

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [URL Structure](#url-structure)
- [API Overview](#api-overview)
- [Database](#database)
- [Core Data Models](#core-data-models)
- [Features](#features)
- [Integration with Core](#integration-with-core)
- [Notes for Developers](#notes-for-developers)

---

## Overview

The Wiki Service, developed by Team NullTerminated, is a structured
content management module designed to handle geographical and
informational articles within the main system.

This service provides a complete article lifecycle management system,
including categorization, tagging, revision history tracking,
internal article linking, reference management, reporting mechanisms,
and user interaction features such as following articles and
receiving notifications.

It is implemented as a dedicated Django application integrated
within the Core system and operates under the unified project
architecture.

---

## Architecture

The Wiki Service is implemented as a dedicated Django application
within the Core system and follows the service-oriented architecture
defined for the overall platform.

It is mounted under the `/team6/` URL namespace,
allowing it to operate as a modular component
while remaining fully integrated with the Core routing
and authentication system.

All components are executed inside Docker containers.
The Core container hosts the Django runtime and executes
the Wiki application.

Although a gateway configuration exists in the project template,
the current implementation relies directly on the Core routing system.

During development, the service operates using Django's
default database configuration within the project environment.

### System Architecture Diagram

```
Browser
   │
   ▼
Core (Django - Port 8000)
   │
   ├── /team6/
   │      ├── Models
   │      ├── Views
   │      ├── Services
   │      └── Templates
   │
   ▼
Database (Project Default Configuration)
```

---

## Project Structure

The Team6 module is organized as a standard Django application
with a clear separation of concerns between models, views,
services, templates, and routing.

```
team6/
├── models.py              # Data models (articles, tags, categories, revisions, etc.)
├── views.py               # Core view logic and request handling
├── urls.py                # URL routing for the service
├── services/              # Internal service logic (search, notifications, etc.)
├── templates/team6/       # HTML templates
├── migrations/            # Database schema migrations
├── templatetags/          # Custom template utilities
├── gateway.conf           # Template Nginx configuration (not actively customized)
└── README.md              # Service documentation
```

The service follows Django best practices by separating
business logic from routing and presentation layers,
ensuring maintainability and scalability.

---

## How to Run

The project is containerized using Docker and can be executed using the provided shell scripts.

To start the entire system (Core + all team services):

```
./linux_scripts/up-all.sh
```

After successful startup, the Core service will be available at:

http://localhost:8000/

The Wiki Service (Team6) can be accessed via:

http://localhost:8000/team6/

Note: The Wiki application itself runs inside the Core container and is mounted under the `/team6/` route.

---

## URL Structure

The Wiki Service is mounted under:

- `/team6/`

Key routes:

- `GET /team6/` — Article list (home page)
- `GET /team6/ping/` — Health check
- `GET /team6/create/` — Create new article
- `GET /team6/article/<slug>/` — Article details
- `GET /team6/article/<slug>/edit/` — Edit an article
- `GET /team6/article/<slug>/delete/` — Delete an article
- `GET /team6/article/<slug>/revisions/` — List article revisions
- `GET /team6/article/<slug>/revisions/<revision_no>/` — View a specific revision
- `GET /team6/article/<slug>/report/` — Report an article
- `GET /team6/article/<slug>/follow/` — Follow/unfollow an article
- `GET /team6/article/<slug>/toggle-notify/` — Toggle notifications for an article
- `GET /team6/notifications/` — Notifications list
- `POST /team6/api/wiki/content` — External API to fetch wiki content
- `POST /team6/api/preview-ai/` — Preview generated content

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | `/team6/` | List articles |
| GET | `/team6/article/<slug>/` | Retrieve article details |
| GET | `/team6/article/<slug>/revisions/` | List article revisions |
| GET | `/team6/notifications/` | Retrieve user notifications |
| POST | `/team6/api/wiki/content` | Fetch external wiki content |
| POST | `/team6/api/preview-ai/` | Preview generated content |

---

## Database

The Wiki Service relies on Django's ORM for data modeling and persistence.

All core entities — including articles, categories, tags, revisions,
references, reports, follows, and notifications — are defined as
structured Django models within the Team6 application.

During development, the service operates using the project's default
database configuration.

Database schema changes are managed through Django migrations
located in the `migrations/` directory.

---

## Core Data Models

| Model | Description |
|-------|------------|
| WikiCategory | Hierarchical article categorization |
| WikiTag | Tagging system with relational support |
| WikiArticle | Main article entity |
| WikiArticleRevision | Revision history tracking |
| WikiArticleLink | Internal article linking |
| WikiArticleRef | External reference management |
| WikiArticleReports | Article reporting mechanism |
| ArticleFollow | User follow system |
| ArticleNotification | Notification management |

---

## Features

The Wiki Service provides a comprehensive set of features for structured article management:

### Article Management
- Create, edit, and delete articles
- Structured fields including titles, summaries, body content, and featured image
- Slug-based routing for clean URLs

### Categorization & Tagging
- Hierarchical categories
- Tag assignment and relationship support
- Flexible content organization

### Revision System
- Full revision history tracking
- Version comparison and restoration support
- Editor tracking per revision

### Article Linking & References
- Internal article-to-article linking
- External reference management
- Structured citation storage

### User Interaction
- Article follow/unfollow functionality
- Notification system for updates
- Article reporting mechanism

### System Utilities
- Health check endpoint
- External content API access
- Preview endpoint for assisted content generation

---

## Integration with Core

The Wiki Service is fully integrated with the Core system.

Authentication and user session management are handled centrally
by the Core service. The Wiki module relies on this shared
authentication mechanism to identify users and enforce access control.

Routing is managed through the Core URL configuration,
which mounts the Wiki Service under the `/team6/` namespace.

The service operates as a modular Django application
while sharing the same runtime environment and infrastructure
as the rest of the system.

---

## Notes for Developers

- The Wiki Service follows Django best practices for modular application design.
- Business logic is separated from routing and presentation layers.
- URL routing is defined within the Team6 module and mounted by the Core system.
- Schema changes must be handled through Django migrations.
- The service is designed to be extendable without affecting the Core infrastructure.

Future enhancements can be implemented within the existing modular structure
without requiring architectural changes to the overall system.
