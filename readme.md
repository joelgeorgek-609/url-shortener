URL Shortener (FastAPI + Keycloak + PostgreSQL)

A simple internal URL shortener service built with FastAPI.
Authenticated users can create and manage short URLs, while anyone can access a short link without authentication.

Features

User authentication using Keycloak (OIDC + JWT)
Create short URLs (protected)
List user’s URLs (protected)
Delete URL (protected, owner only)
Public redirect endpoint
PostgreSQL database using SQLAlchemy ORM
Pydantic v2 for request/response validation
Environment-based configuration

Setup Instructions

Create and activate virtual environment:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PostgreSQL Setup

In psql:

CREATE DATABASE shortener_db;
CREATE USER shortener_user WITH PASSWORD 'mysecret';
GRANT ALL PRIVILEGES ON DATABASE shortener_db TO shortener_user;

Environment Variables

Create a .env file:

DATABASE_URL=postgresql+psycopg2://shortener_user:mysecret@localhost:5432/shortener_db
KEYCLOAK_ISSUER=http://localhost:8080/realms/shortener


KEYCLOAK_CLIENT_ID=shortener-client
SERVICE_BASE_URL=http://localhost:8000


DISABLE_AUDIENCE_CHECK=true

Keycloak Setup (Quick Guide)

Start Keycloak in dev mode:

docker run -d --name keycloak
-p 8080:8080
-e KEYCLOAK_ADMIN=admin
-e KEYCLOAK_ADMIN_PASSWORD=admin
quay.io/keycloak/keycloak:24.0.5 start-dev

Go to Keycloak admin UI:
http://localhost:8080

Create Realm:
shortener

Create Client:

Client ID: shortener-client

Type: OpenID Connect

Direct Access Grants: Enabled

Valid Redirect URIs: *

Web Origins: *

Create Realm Role:
user

Create User:

Set username and password

Disable temporary password

Assign the "user" role

Running the Application

Start FastAPI:

uvicorn app.main:app --reload --port 8000

Open API docs:
http://localhost:8000/docs

API Usage (curl)

Get Access Token:

curl -X POST "http://localhost:8080/realms/shortener/protocol/openid-connect/token

"
-H "Content-Type: application/x-www-form-urlencoded"
-d "grant_type=password"
-d "client_id=shortener-client"
-d "username=<USER>"
-d "password=<PASS>"

Copy "access_token" from the response.

Create Short URL (Protected)

curl -X POST "http://localhost:8000/shorten

"
-H "Authorization: Bearer <ACCESS_TOKEN>"
-H "Content-Type: application/json"
-d '{"url": "https://google.com"}

'

List User URLs (Protected)

curl -X GET "http://localhost:8000/urls

"
-H "Authorization: Bearer <ACCESS_TOKEN>"

Delete URL (Owner Only)

curl -X DELETE "http://localhost:8000/urls/

<ID>"
-H "Authorization: Bearer <ACCESS_TOKEN>"

Access Short URL (Public)

curl -I "http://localhost:8000/

<short_code>"