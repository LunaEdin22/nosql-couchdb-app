# NoSQL Cloud Store API (Apache CouchDB + FastAPI)

A production-ready microservice built with **FastAPI** and **Apache CouchDB** demonstrating modern NoSQL document database principles, dynamic JSON schemas, and automated CI/CD cloud deployment.

---

## Architecture & Features

- **Database:** Apache CouchDB 3.3 (Document NoSQL store with native HTTP REST API and Fauxton Web Dashboard).
- **Backend:** Python 3.12 + FastAPI with interactive Swagger UI (`/docs`).
- **Containerization:** Multi-stage Docker build with Docker Compose support.
- **CI/CD Automation:** GitHub Actions pipeline with automated integration tests against an isolated CouchDB service container.
- **Public Cloud Deployment:** Compatible with Railway, Render, Koyeb, and Azure App Service.

---

## Live Cloud Deployment & Video Demo

- **Video Walkthrough (YouTube):** [https://youtu.be/rKqgC9_2xaw](https://youtu.be/rKqgC9_2xaw)
- **Public Interactive Docs (Swagger):** [https://volt-mere-inputs-nothing.trycloudflare.com/docs](https://volt-mere-inputs-nothing.trycloudflare.com/docs)
- **Public API Root:** [https://volt-mere-inputs-nothing.trycloudflare.com/](https://volt-mere-inputs-nothing.trycloudflare.com/)
- **Public Products Endpoint:** [https://volt-mere-inputs-nothing.trycloudflare.com/products](https://volt-mere-inputs-nothing.trycloudflare.com/products)
- **Database Engine:** Apache CouchDB 3.3 (Document NoSQL Store)

---

## Quickstart (Local Development)

### 1. Run with Docker Compose
The easiest way to start both CouchDB and the FastAPI app:
```bash
docker compose up --build -d
```

### 2. Access the Services
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)
- **CouchDB Fauxton Dashboard:** [http://localhost:5984/_utils/](http://localhost:5984/_utils/)
  - *User:* `admin`
  - *Password:* `password`

### 3. Seed Sample Data
Execute the seeding endpoint to populate sample products:
```bash
curl -X POST http://localhost:8000/products/seed
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and metadata |
| `GET` | `/health` | Healthcheck and CouchDB connectivity check |
| `GET` | `/products` | List all documents with pagination |
| `POST` | `/products` | Create a new document with dynamic specs |
| `GET` | `/products/{id}` | Retrieve document by ID |
| `PUT` | `/products/{id}` | Update document (handles CouchDB MVCC `_rev`) |
| `DELETE` | `/products/{id}` | Remove document from CouchDB |
| `GET` | `/products/category/{cat}` | Filter documents using CouchDB Mango query |
| `POST` | `/products/seed` | Seed initial tech store dataset |

---

## Running Integration Tests

```bash
# Install dependencies
pip install -r app/requirements.txt

# Run pytest against running service
pytest scripts/test_api.py -v
```

---

## Cloud Deployment (Railway / Render)

1. Push this repository to GitHub.
2. In **Railway** (or **Render**):
   - Create a new project from your GitHub repository.
   - Add a CouchDB template / service or deploy with the provided Dockerfile.
   - Set environment variables (`COUCHDB_HOST`, `COUCHDB_USER`, `COUCHDB_PASSWORD`, `COUCHDB_DB_NAME`).
3. Every `git push` to `main` automatically runs tests in GitHub Actions and updates your live cloud service!
