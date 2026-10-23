

The project structure is organized by **Bounded Context & Business Domain**, rather than arbitrary horizontal technical layers. This guarantees **high cohesion**, **loose coupling**, and seamless scalability for enterprise systems:

```text
book-finder-app/
├── core/                           # ⚙️ Platform Kernel (Config, Constants, Errors, Logging)
│   ├── __init__.py
│   ├── config.py                   # Multi-environment configurations (Dev, Staging, Prod)
│   ├── constants.py                # Centralized semantic constants (No magic numbers/strings)
│   ├── errors.py                   # Global error handlers & domain exceptions
│   └── logger.py                   # Centralized structured logging provider
│
├── infrastructure/                 # 🌐 External I/O, Database & Network Services
│   ├── __init__.py
│   ├── database.py                 # MongoDB DatabaseManager & Index Management
│   └── http_client.py              # Centralized BaseHttpClient with Keep-Alive pooling
│
├── app/                            # 🚀 Application Package (Feature & Presentation)
│   ├── __init__.py                 # Application Factory Pattern & Health Check Endpoint
│   │
│   ├── books/                      # 📖 Feature Module: Catalog Search & Remote APIs
│   │   ├── __init__.py
│   │   ├── models.py               # Pure Domain Entity (Book - Zero vendor dependency)
│   │   ├── schemas.py              # Response Schema (BookSchema) & DTOs
│   │   ├── repository.py           # BookRepository (Data Access & Failover Orchestration)
│   │   ├── service.py              # BookService & GoogleBooksGateway (HTTP client)
│   │   ├── routes.py               # Controller Endpoints (/api/search)
│   │   └── tests/                  # 🧪 Unit Tests (Strict Mocks - Pure Unit Tests)
│   │       ├── __init__.py
│   │       ├── test_service.py     # Unit tests: Service, Repository, Gateway, & Entities
│   │       └── test_routes.py      # Unit tests: Controller endpoints (/api/search)
│   │
│   ├── wishlist/                   # 💖 Feature Module: Personal Wishlist Management
│   │   ├── __init__.py
│   │   ├── models.py               # Pure Domain Entity (WishlistItem)
│   │   ├── schemas.py              # Request & Response Schema (WishlistItemSchema)
│   │   ├── repository.py           # MongoWishlistRepository (MongoDB Persistence)
│   │   ├── service.py              # WishlistService (CRUD Logic & Invariant Validation)
│   │   ├── routes.py               # Controller Endpoints (/api/wishlist)
│   │   └── tests/                  # 🧪 Unit Tests (Strict Mocks - Pure Unit Tests)
│   │       ├── __init__.py
│   │       ├── test_service.py     # Unit tests: Service, Repository, & Models
│   │       └── test_routes.py      # Unit tests: Controller endpoints (/api/wishlist)
│   │
│   └── views/                      # 🖥️ Presentation Module: Web UI (Self-Contained)
│       ├── __init__.py
│       ├── routes.py               # Render main landing view (index.html)
│       ├── templates/              # HTML Templates
│       │   └── index.html
│       ├── static/                 # Static Assets (CSS / JavaScript)
│       │   ├── css/
│       │   │   └── style.css
│       │   └── js/
│       │       └── main.js
│       └── tests/                  # 🧪 Unit Tests for presentation module
│           ├── __init__.py
│           └── test_views.py       # Unit tests: Index route & Health Check probe
│
├── .dockerignore                   # Docker build context optimization
├── .gitignore                      # Git cache and environment exclusions
├── Dockerfile                      # Python 3.10-slim container specification
├── docker-compose.yml              # Multi-container orchestration (Web app on 5001 + MongoDB)
├── Makefile                        # DevEx automation (make up, make test, make logs, make down)
├── requirements.txt                # Production dependencies (Flask, Requests, PyMongo)
├── run.py                          # Application entry point
├── test_app.py                     # Test discovery runner (52 Unit Tests)
└── README.md                       # Project documentation
```

---

## 🌟 Key Architectural Highlights & Engineering Decisions

1. **Package-by-Feature (DDD)**: Each domain module (`books`, `wishlist`, `views`) is a self-contained bounded context. If a feature needs to be extracted into a standalone microservice in the future, the directory can be moved with minimal friction.
2. **Decoupled Domain Entities & Schemas**: Business logic operates strictly on pure domain entities (`Book`, `WishlistItem`), insulated from transport formatting and database representations.
3. **Graceful Degradation & Network Optimization**: 
   - Primary catalog queries target the Google Books API. If empty or unavailable, the system automatically falls back to Open Library.
   - `BaseHttpClient` uses `requests.Session` with Keep-Alive connection pooling and selective field querying (`fields=key,title,...`), reducing Open Library latency from ~10 seconds down to ~1-2 seconds.
4. **Database Idempotency & $O(1)$ Indexing**: `MongoWishlistRepository` performs idempotent upserts with an enforced unique index on `id`, preventing duplicate records during network retries.
5. **Strict Mock Unit Testing (Go `mockery` Style)**: 
   - All tests use Python's `unittest.mock.create_autospec` to strictly validate method existence and parameter signatures.
   - Zero reliance on live databases or external network calls ensures fast, reliable CI/CD runs (**52 test cases complete in ~0.09s**).
6. **Liveness & Readiness Health Probe**: Standardized `/health` and `/api/health` endpoints inspect application status and ping MongoDB.

---

## 🌐 Multi-Environment Configuration (12-Factor App)

The application follows the **12-Factor App** methodology with explicit environment segregation:

| Environment | Variable (`FLASK_ENV` / `APP_ENV`) | Config File | Class in `core/config.py` | MongoDB Database | Debug Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development** | `dev` / `development` | `.env.development` | `DevelopmentConfig` | `book_finder_dev` | `True` (Hot-reload) |
| **Staging / UAT** | `stg` / `staging` | `.env.staging` | `StagingConfig` | `book_finder_staging` | `False` (Detailed logs) |
| **Production** | `prd` / `production` | `.env.production` | `ProductionConfig` | `book_finder_prod` | `False` (Secure Cookies) |

### Running by Environment:

#### 1. Via Command Line (CLI)
The configuration engine automatically resolves environment aliases (`stg`, `prd`, `dev`):
```bash
# Run in Development mode
FLASK_ENV=dev python run.py

# Run in Staging (UAT) mode
FLASK_ENV=stg python run.py

# Run in Production mode
FLASK_ENV=prd python run.py
```

#### 2. Via Docker Compose
Specify the environment file directly:
```bash
docker-compose --env-file .env.staging up -d --build
```

---

## 🚀 Getting Started

### Step 1: Environment Setup
Clone the repository and copy the environment template:
```bash
cp .env.example .env
```
*(The `.env.example` file contains preconfigured defaults ready for immediate use).*

---

### Option 1: Running with Docker Compose & Makefile (Recommended)

Ensure Docker Desktop or OrbStack is running.

1. **Start Containers in Detached Mode:**
   ```bash
   make up
   # or: docker-compose up -d --build
   ```

2. **Access the Web Application:**
   👉 **[http://localhost:5001](http://localhost:5001)**
   *(Host port `5001` is mapped to container port `5000` to prevent conflicts with macOS AirPlay Receiver).*

3. **Inspect Application Logs:**
   ```bash
   make logs
   # or: docker-compose logs -f
   ```

4. **Stop Containers:**
   ```bash
   make down
   # or: docker-compose down
   ```

---

### Option 2: Running Locally (Without Docker)

1. **Ensure Local MongoDB is Running:**
   Active MongoDB instance accessible at `mongodb://localhost:27017/`.

2. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application:**
   ```bash
   python run.py
   ```

5. **Access:**
   👉 **[http://localhost:5001](http://localhost:5001)**

---

## 📡 API Endpoints Documentation

| Method | Endpoint | Description | Query / Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Web UI Landing Page (Presentation Layer) | None | `200 OK` |
| `GET` | `/health` / `/api/health` | Health Check Liveness & Readiness Probe | None | `200 OK` (Healthy) / `200 OK` (Degraded) |
| `GET` | `/api/search` | Search book catalog via Google Books & Open Library | Query: `?q=<keyword>` | `200 OK` |
| `GET` | `/api/wishlist` | Retrieve all saved wishlist items | None | `200 OK` |
| `POST` | `/api/wishlist` | Add a book to personal MongoDB wishlist | JSON: `{ id, title, authors, thumbnail, rating, ... }` | `201 Created` / `400 Bad Request` |
| `DELETE` | `/api/wishlist/<id>` | Remove a book from wishlist by ID | Path param: `<id>` | `200 OK` / `404 Not Found` |

---

## 🧪 Running Unit Tests

The test suite adopts **Pure Unit Testing** with **Strict Mocking** (`create_autospec` - Go `mockery` style), isolating business logic from live network requests and databases.

Every module (`books`, `wishlist`, `views`) includes both **Positive (Happy Path)** and **Negative (Edge Cases, Validation Errors, Failures)** test suites.

```bash
# Run all 52 unit test cases via Makefile (Recommended):
make test

# Or directly via docker-compose:
docker-compose run --rm web python test_app.py

# Or in a local Python environment:
python test_app.py
```

### Test Suite Execution Output:
```text
Ran 52 tests in 0.094s

OK
```
All 52 tests execute deterministically in **~94 milliseconds**.
