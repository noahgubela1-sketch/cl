# SceneMind AI – API Reference (v1)

Base URL: `http://localhost:8000/api/v1`

Interactive docs: http://localhost:8000/docs (Swagger UI)

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### `POST /auth/register`
Register a new account.

**Body:**
```json
{ "email": "user@example.com", "password": "secret123", "full_name": "Jane" }
```

**Response:** `201 Created`
```json
{ "access_token": "...", "token_type": "bearer" }
```

---

### `POST /auth/login`
Obtain an access token.

**Response:** `200 OK` – same as register.

---

### `GET /auth/me`
Return current user info.

---

## Projects

### `POST /projects/`
Create a new project.

### `GET /projects/`
List all projects owned by the current user.

### `GET /projects/{id}`
Get project details.

### `PATCH /projects/{id}`
Update project metadata.

### `DELETE /projects/{id}`
Delete a project.

---

## Scripts

### `POST /scripts/{project_id}/upload`
Upload a screenplay file (PDF, FDX, Fountain, Celtx).

Returns `202 Accepted` immediately; parsing runs as a background task.

### `GET /scripts/{project_id}/scripts`
List uploaded scripts for a project.

---

## Scheduling

### `POST /schedules/{project_id}/generate`
Trigger AI schedule generation (async background task).

### `GET /schedules/{project_id}/scenes`
List all parsed scenes for a project.

### `PATCH /schedules/{project_id}/scenes/{scene_id}`
Manually update a scene (location, estimated time, priority, etc.).

### `GET /schedules/{project_id}/shooting-days`
List generated shooting days in chronological order.

---

## Live Tracking

### `POST /tracking/events`
Log a tracking event (scene_start, scene_end, break_start, etc.).

### `GET /tracking/events/{shooting_day_id}`
Get all tracking events for a shooting day.

### `WebSocket /tracking/ws/{shooting_day_id}`
Subscribe to real-time events for a shooting day.

---

## Exports

### `GET /export/{project_id}/pdf`
Download shooting schedule as PDF.

### `GET /export/{project_id}/xlsx`
Download as Excel spreadsheet.

### `GET /export/{project_id}/ical`
Download as iCalendar file (compatible with Google Calendar, Apple Calendar, Outlook).
