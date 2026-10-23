---
title: Book Finder App
emoji: 📖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Book Finder App

A full-stack book catalog search and personal wishlist management web application built with Python (Flask) and MongoDB.

[![CI Test Suite](https://github.com/GieGieapp/book-finder-app/actions/workflows/ci.yml/badge.svg)](https://github.com/GieGieapp/book-finder-app/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-success?style=flat&logo=vercel)](https://book-finder-app-ochre.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black?logo=flask)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://www.mongodb.com/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-52%20Passed-brightgreen)](#testing)

---

## Live Application

The production application is deployed and publicly accessible:
- **Live Demo:** [https://book-finder-app-ochre.vercel.app/](https://book-finder-app-ochre.vercel.app/)
- **API Health Check:** [https://book-finder-app-ochre.vercel.app/health](https://book-finder-app-ochre.vercel.app/health)

---

## Project Structure

```text
book-finder-app/
├── core/                           # Platform kernel (config, constants, errors, logging)
│   ├── __init__.py
│   ├── config.py                   # Environment configuration
│   ├── constants.py                # Semantic constants and defaults
│   ├── errors.py                   # Error handlers and domain exceptions
│   └── logger.py                   # Structured logging setup
│
├── infrastructure/                 # External I/O and database services
│   ├── __init__.py
│   ├── database.py                 # MongoDB connection and indexing
│   └── http_client.py              # HTTP client with Keep-Alive pooling
│
├── app/                            # Application modules
│   ├── __init__.py                 # Application factory and health check route
│   │
│   ├── books/                      # Book catalog search module
│   │   ├── __init__.py
│   │   ├── models.py               # Book domain entity
│   │   ├── schemas.py              # Book response schemas
│   │   ├── repository.py           # Catalog repository with failover
│   │   ├── service.py              # Search use case and API gateway
│   │   ├── routes.py               # Search controller (/api/search)
│   │   └── tests/                  # Unit tests (positive & negative cases)
│   │       ├── __init__.py
│   │       ├── test_service.py     # Service, repository, and gateway tests
│   │       └── test_routes.py      # Route tests
│   │
│   ├── wishlist/                   # Wishlist management module
│   │   ├── __init__.py
│   │   ├── models.py               # WishlistItem domain entity
│   │   ├── schemas.py              # Wishlist response schemas
│   │   ├── repository.py           # MongoDB wishlist repository
│   │   ├── service.py              # Wishlist service logic
│   │   ├── routes.py               # Wishlist controller (/api/wishlist)
│   │   └── tests/                  # Unit tests (positive & negative cases)
│   │       ├── __init__.py
│   │       ├── test_service.py     # Service, repository, and model tests
│   │       └── test_routes.py      # Route tests
│   │
│   └── views/                      # Presentation module
│       ├── __init__.py
│       ├── routes.py               # Web view controller (/)
│       ├── templates/              # HTML templates
│       ├── static/                 # CSS and JavaScript assets
│       └── tests/                  # Unit tests
│           ├── __init__.py
│           └── test_views.py       # View and health check tests
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── Makefile
├── requirements.txt
├── run.py
├── test_app.py
└── README.md
```

---

## Key Architectural Decisions

1. **Package-by-Feature (DDD)**: Code is organized around business features (`books`, `wishlist`, `views`) rather than horizontal technical layers, ensuring high cohesion and low coupling.
2. **Entity and Schema Separation**: Domain entities (`Book`, `WishlistItem`) handle business logic and remain decoupled from HTTP serialization schemas.
3. **Graceful Failover**: Book queries prioritize Google Books API and automatically fall back to Open Library API when queries return empty.
4. **Network Optimization**: `BaseHttpClient` uses `requests.Session` Keep-Alive pooling to reuse TCP connections, with field filtering applied on external APIs to reduce response latency.
5. **Database Indexing and Idempotency**: The MongoDB wishlist collection enforces a unique index on `id` for O(1) lookups and idempotent upserts.
6. **Strict Mock Unit Testing**: All 52 unit tests use `unittest.mock.create_autospec` to validate interface contracts without touching live databases or networks.

---

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
```

### 2. Run with Docker Compose

```bash
make up
# or: docker-compose up -d --build
```

Access the application in your browser at `http://localhost:5001`.

Useful Makefile commands:
- `make logs`: View container logs
- `make down`: Stop running containers
- `make test`: Run all unit tests

### 3. Run Locally (Without Docker)

Ensure a local MongoDB instance is running at `mongodb://localhost:27017/`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

---

## API Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Web UI landing page | `200 OK` |
| `GET` | `/health` | Health check probe (liveness & readiness) | `200 OK` |
| `GET` | `/api/search` | Search book catalog (Google Books + Open Library) | `200 OK` |
| `GET` | `/api/wishlist` | Retrieve all saved wishlist items | `200 OK` |
| `POST` | `/api/wishlist` | Add a book to personal wishlist | `201 Created` / `400 Bad Request` |
| `DELETE` | `/api/wishlist/<id>` | Remove a book from wishlist by ID | `200 OK` / `404 Not Found` |

---

## Running Tests

All 52 tests are pure unit tests covering positive and negative cases:

```bash
# Run tests inside Docker container:
make test

# Or run locally:
python test_app.py
```
