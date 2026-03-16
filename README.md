# 🐾 Pet Insurance Reimbursement Platform

A full-stack application for managing pet insurance reimbursement claims.

## Tech Stack

> 📘 **For a detailed guide on how the app works for each role (Customer, Support, Admin), see [GUIDE.md](GUIDE.md).**

| Layer | Technology |
|---|---|
| Backend | Django 4.2 + Django REST Framework |
| Async tasks | Celery + Redis |
| Frontend | Vue.js 3 + Pinia + Vue Router |
| API Docs | drf-spectacular (Swagger / ReDoc) |
| Containers | Docker + docker-compose |

---

## Quick Start

### Prerequisites
- Docker & docker-compose installed

### Run with Docker

```bash
# Clone the repository
git clone <repo-url>
cd pet-insurance

# Start all services
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost/api/ |
| Swagger Docs | http://localhost/api/docs/ |
| ReDoc | http://localhost/api/redoc/ |
| Django Admin | http://localhost/admin/ |

### Create a superuser (optional)

```bash
docker-compose exec backend python manage.py createsuperuser
```

---

## Running Locally (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # Edit as needed (point Redis to localhost)

python manage.py migrate
python manage.py runserver
```

### Celery Worker

```bash
# In a separate terminal (with venv activated)
cd backend
celery -A config worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Architecture

### Claim Processing Flow

```
Customer submits claim
        │
        ▼
  Status → PROCESSING  (immediate, synchronous)
        │
        ▼
  Celery task dispatched  ──────────────────────────┐
        │                                           │
        ▼                                           ▼
  Simulate invoice extraction (2s delay)     If invalid date_of_event
        │                                    Status → REJECTED
        ▼
  Validate date_of_event within coverage
        │
        ▼
  Status → IN_REVIEW
        │
        ▼
  Support reviews → APPROVED or REJECTED
```

### Role-Based Access

| Role | Capabilities |
|---|---|
| `CUSTOMER` | Register pets, submit claims, view own data |
| `SUPPORT` | View all claims, approve/reject IN_REVIEW claims |
| `ADMIN` | All of the above + Django admin |

---

## API Endpoints

### Auth
```
POST  /api/auth/register/       Register new user
POST  /api/auth/login/          Obtain JWT tokens
POST  /api/auth/token/refresh/  Refresh access token
GET   /api/auth/me/             Get current user
```

### Pets
```
GET    /api/pets/          List pets
POST   /api/pets/          Create pet
GET    /api/pets/{id}/     Retrieve pet
PUT    /api/pets/{id}/     Update pet
DELETE /api/pets/{id}/     Delete pet
```

### Claims
```
GET    /api/claims/              List claims (filtered by role)
POST   /api/claims/              Submit new claim (multipart/form-data)
GET    /api/claims/{id}/         Retrieve claim
PATCH  /api/claims/{id}/review/  Approve/reject claim (Support/Admin only)
```

### Query filters for claims
- `?status=IN_REVIEW`
- `?pet=<id>`
- `?created_after=2024-01-01`
- `?created_before=2024-12-31`

---

## Business Rules

- `coverage_end = coverage_start + 365 days`
- `invoice_date` must fall within the pet's coverage period
- `date_of_event` must fall within the pet's coverage period (validated by Celery task)
- Duplicate invoices are detected via SHA-256 file hash

---

## Development Mode (Hot Reload)

Start all services with Vite dev server and hot reload:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

| Service | URL |
|---|---|
| Frontend (Vite + HMR) | http://localhost:5173 |
| Backend API | http://localhost:5173/api/ |
| Swagger Docs | http://localhost:5173/api/docs/ |
| ReDoc | http://localhost:5173/api/redoc/ |
| Django Admin | http://localhost:5173/admin/ |

Any changes in `frontend/src/` are reflected instantly without rebuild.

## Production Mode

Full build with Nginx serving the frontend:

```bash
docker-compose up --build -d
```

| Service | URL |
|---|---|
| Frontend (Nginx) | http://localhost |
| Backend API | http://localhost/api/ |
| Swagger Docs | http://localhost/api/docs/ |
| ReDoc | http://localhost/api/redoc/ |
| Django Admin | http://localhost/admin/ |

---

## Running Tests

```bash
cd backend
python manage.py test apps.claims.tests
```

---

## Project Structure

```
pet-insurance/
├── backend/
│   ├── apps/
│   │   ├── users/       # Auth, JWT, roles
│   │   ├── pets/        # Pet CRUD, permissions
│   │   └── claims/      # Claim workflow, Celery tasks, tests
│   ├── config/          # Django settings, URLs, Celery config
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/       # LoginView, PetsView, ClaimsView, ReviewView, ...
│   │   ├── store/       # Pinia (auth)
│   │   ├── router/      # Vue Router with guards
│   │   └── services/    # Axios instance
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```
