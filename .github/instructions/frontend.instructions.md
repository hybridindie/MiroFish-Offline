---
description: Frontend-only guidance for Vue components, routing, and API wrapper usage in this repository.
applyTo: "frontend/**"
---

# Frontend Guidelines

## Build And Test
- Start frontend only: `npm run frontend`
- Build frontend: `npm run build`

## Architecture
- Frontend is a Vue 3 + Vite SPA in `frontend/src`.
- View-level pages live in `frontend/src/views`.
- Reusable UI components live in `frontend/src/components`.
- API modules live in `frontend/src/api`.
- Router configuration lives in `frontend/src/router/index.js`.

## Conventions
- Use existing API wrapper patterns in `frontend/src/api/index.js` (axios instance, interceptor handling, retry helper).
- Keep long-running backend operations compatible with current timeout and retry behavior in the API layer.
- Follow existing route and component organization patterns used across `frontend/src/router` and `frontend/src/views`.
- Prefer composition patterns already present in this codebase's Vue Single File Components.

## Environment And Pitfalls
- Do not hardcode backend hosts directly in view components; route requests through API modules.
- Preserve user-facing text behavior and existing navigation flows when refactoring screens.

## Key Reference Files
- Commands: `frontend/package.json`
- App entry: `frontend/src/main.js`, `frontend/src/App.vue`
- Router: `frontend/src/router/index.js`
- API wrapper patterns: `frontend/src/api/index.js`