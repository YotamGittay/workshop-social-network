# Workshop Social Network — Design

Date: 2026-09-15
Status: Approved by user

## Goal

Simple demo social network, fully Docker-based, running locally via one `docker compose up --build`.
Four services: SQL database, blob storage, FastAPI backend, React frontend.

## Decisions (from brainstorming)

- **DB**: Postgres (`postgres:16-alpine`) — simpler Docker config than MySQL.
- **Blob storage**: MinIO (open-source, S3-compatible, standard image) + one-shot `mc` init container that creates bucket `images` and sets it public-read.
- **Identity**: user switcher, no passwords. Client sends `X-User-Id` header. Seeded users.
- **Scope**: minimal — follow, unfollow, create post (text + optional image), feed of last 10 posts from followees. No likes/comments.
- **Frontend serving**: production build (Vite) served by nginx; nginx also reverse-proxies `/api/` → backend and `/images/` → MinIO. No CORS issues, single origin.

## Architecture

```
browser
  │ http://localhost:3000
  ▼
frontend (nginx:alpine, static React build)
  ├── /api/*    → backend:8000
  └── /images/* → blob:9000/images/*
backend (FastAPI, python:3.12-slim)
  ├── SQLAlchemy → db (postgres:16-alpine)
  └── boto3      → blob (minio/minio)
blob-init (minio/mc, one-shot): create bucket `images`, anonymous download
urls (alpine, one-shot): prints access URLs to compose logs
```

Ports: frontend `3000`, backend `8000` (debug), MinIO console `9001`.

## Data model

- `users(id PK, username UNIQUE, display_name)`
- `follows(follower_id FK, followee_id FK, PK(follower_id, followee_id))`
- `posts(id PK, author_id FK, text, image_key NULL, created_at)` — `image_key` is the MinIO object key; index on `created_at`.

## API (all authed routes require `X-User-Id` header)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | liveness |
| GET | `/api/users` | list all users (switcher + follow list) |
| GET | `/api/users/me/following` | users I follow |
| POST | `/api/follows/{user_id}` | follow (idempotent; 400 on self-follow) |
| DELETE | `/api/follows/{user_id}` | unfollow (idempotent) |
| GET | `/api/feed` | last 10 posts by followees, newest first |
| POST | `/api/posts` | multipart `text` + optional `image`; stores image in MinIO |

Post JSON: `{id, text, image_url, created_at, author:{id, username, display_name}}`.
`image_url` = `/images/{key}` (relative, resolved by nginx).

## Frontend

React 18 + Vite, plain CSS, no UI library.

- Header: "who am I" dropdown (persisted in `localStorage`).
- Sidebar: all users with Follow/Unfollow buttons.
- Main: new-post box (textarea + optional image file), feed below.
- Feed polls every 5 s. Relative timestamps. Empty-state message.

## Startup & seeding

- Compose `depends_on` with healthchecks: db (`pg_isready`), blob (`mc ready local`), blob-init completed before backend.
- Backend on startup: `create_all`, then seed if `users` empty — 5 users (alice, bob, carol, dave, erin), ~8 follows, ~14 posts with staggered timestamps so the feed is non-empty.

## Error handling

- Uploads: only jpeg/png/gif/webp, max 5 MB (enforced in backend; nginx `client_max_body_size 6m`).
- 401 for missing/unknown `X-User-Id`; 404 unknown target user; 400 self-follow / empty text / bad image.
- Backend retries DB connect on startup (defense in depth beyond healthchecks).

## Testing

Manual smoke script after `up`: list users → follow → create text post → create image post → feed contains both → image URL returns 200 via nginx → unfollow removes from feed.
