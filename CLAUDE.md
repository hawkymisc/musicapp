# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is an indie music platform with two main components:
- **Backend**: FastAPI app with PostgreSQL database, Firebase auth, S3 storage, Stripe payments
- **Frontend**: React/Vite app with React Router, context-based state management

Key architectural patterns:
- Backend follows FastAPI service layer pattern with SQLAlchemy ORM and Pydantic schemas
- Frontend uses React functional components with hooks and context providers for state
- Authentication via Firebase with JWT tokens passed in Authorization headers
- File uploads to AWS S3 for audio and cover art storage
- Database migrations managed via Alembic

## Build and Run Commands

**Development:**
- Frontend: `cd indie-music-platform-frontend && npm run dev`
- Backend: `cd indie-music-platform-backend && uvicorn app.main:app --reload`

**Docker (full stack):**
- `cd indie-music-platform-backend && docker-compose up -d`
- Includes PostgreSQL database and backend API

**Testing:**
- Backend tests: `cd indie-music-platform-backend && pytest`
- Single backend test: `cd indie-music-platform-backend && pytest tests/path/to/test.py::test_function_name -v`

**Build/Lint:**
- Frontend build: `cd indie-music-platform-frontend && npm run build`
- Frontend lint: `cd indie-music-platform-frontend && npm run lint`

**Database:**
- Create migration: `cd indie-music-platform-backend && alembic revision --autogenerate -m "description"`
- Run migrations: `cd indie-music-platform-backend && alembic upgrade head`
- Create seed data: `cd indie-music-platform-backend && python create_seed_data.py`
- Reset database with seed: `cd indie-music-platform-backend && python reset_database.py --with-seed`
- Minimal test data: `cd indie-music-platform-backend && python minimal_seed_data.py`

**Frontend Testing:**
- Unit tests: `cd indie-music-platform-frontend && npm test`
- E2E tests: `cd indie-music-platform-frontend && npm run test:e2e`
- E2E with UI: `cd indie-music-platform-frontend && npm run test:e2e:ui`

## Key File Locations

**Backend:**
- Main entry: `indie-music-platform-backend/app/main.py`
- API routes: `indie-music-platform-backend/app/api/v1/`
- Services: `indie-music-platform-backend/app/services/`
- Models: `indie-music-platform-backend/app/models/`
- Schemas: `indie-music-platform-backend/app/schemas/`

**Frontend:**
- Main entry: `indie-music-platform-frontend/src/main.jsx`
- Router: `indie-music-platform-frontend/src/router.jsx`
- Pages: `indie-music-platform-frontend/src/pages/`
- Services: `indie-music-platform-frontend/src/services/`
- Contexts: `indie-music-platform-frontend/src/contexts/`

## Configuration

**Environment Files:**
- Backend: `.env` in `indie-music-platform-backend/` (copy from `.env.example`)
- Frontend: Environment variables prefixed with `VITE_`

**Required Services:**
- PostgreSQL database
- AWS S3 bucket for file storage
- Firebase project for authentication
- Stripe account for payments

## Project Purpose

This is an indie music platform (インディーズミュージックプラットフォーム) that enables independent musicians to monetize their music directly without record labels. The platform provides:

**For Artists:**
- Music upload and management with metadata editing
- Direct music sales with artist-controlled pricing
- Revenue dashboard and earnings tracking
- Artist profile management
- Track statistics and play count monitoring

**For Listeners:**
- Music discovery, search, and streaming
- Direct music purchases and downloads
- Personal music library management
- Artist profile browsing

## Core Data Models

**Users**: ID, email, Firebase UID, display name, user role (Artist/Listener), verification status
**Tracks**: ID, artist ID, title, description, genre, cover art URL, audio file URL, duration, price, play count
**Purchases**: ID, user ID, track ID, amount, purchase date, payment method, transaction ID, status

## API Endpoints Structure

All APIs are under `/api/v1/`:
- **Authentication**: `/auth/` (register, login, user management)
- **Tracks**: `/tracks/` (CRUD, search, upload, artist tracks)
- **Users**: `/users/` (profile management)
- **Artists**: `/artists/` (revenue, statistics)
- **Purchases**: `/purchases/` (buying, download history)
- **Streaming**: `/stream/` (playback URLs, play tracking)

## Development Notes

**Revenue Model**: 15% platform commission on direct sales
**File Storage**: Separate endpoints for audio files (`/tracks/upload/audio`) and cover art (`/tracks/upload/cover`)
**Authentication**: Role-based access control with Firebase JWT tokens
**Security**: CORS configured for localhost:3000 and localhost:5173 in development

## Code Style Guidelines
- **Frontend**: React functional components with hooks, camelCase variables, PascalCase components
- **Backend**: FastAPI patterns with SQLAlchemy ORM, snake_case naming, Pydantic schemas
- **Imports**: Standard library, third-party packages, then local modules
- **Error Handling**: try/catch in JS, try/except in Python with proper logging

## Tool Usage Guidelines

When receiving user requests, consider the following approach:
- **First**: Attempt to complete the task using standard CLI tools (bash, git, file operations, etc.)
- **If CLI is insufficient**: Evaluate whether the task can be accomplished using playwright-mcp for web browser automation
- **Examples of playwright-mcp appropriate tasks**: Domain registration, DNS configuration via web interfaces, account setup on web platforms, form submissions that cannot be automated via API

Always prioritize CLI automation when possible, but leverage playwright-mcp when web browser interaction is the most efficient or only viable approach.