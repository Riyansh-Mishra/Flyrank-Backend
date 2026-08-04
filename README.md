# Task API

A CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with FastAPI. Originally used in-memory storage (Week 2); now uses a SQLite database (Week 3) so data survives server restarts.

## How to run

1. Clone this repo and enter the folder:
```bash
   git clone https://github.com/<your-username>/todo-crud-api.git
   cd todo-crud-api
```
2. Create a virtual environment and activate it:
```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
```
3. Install dependencies and run:
```bash
   pip install fastapi uvicorn pydantic
   uvicorn main:app --reload
```
4. Server runs at `http://localhost:8000`. Interactive docs (Swagger UI) at `http://localhost:8000/docs`.
5. On first run, `tasks.db` is created automatically with 3 seeded example tasks.

## Endpoints

| Method | Path            | Description                  | Success | Errors        |
|--------|-----------------|-------------------------------|---------|---------------|
| GET    | `/`             | API info                      | 200     | —             |
| GET    | `/health`       | Health check                  | 200     | —             |
| GET    | `/tasks`        | List all tasks                | 200     | —             |
| GET    | `/tasks/{id}`   | Get one task                  | 200     | 404           |
| POST   | `/tasks`        | Create a task                 | 201     | 400           |
| PUT    | `/tasks/{id}`   | Update a task                 | 200     | 400, 404      |
| DELETE | `/tasks/{id}`   | Delete a task                 | 204     | 404           |
| GET    | `/stats`        | Task counts                   | 200     | —             |

## Example request

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI (Week 2)

![Swagger UI endpoint list](./swagger-screenshot.png)
![Swagger UI request test](./swagger-request-screenshot.png)

## Database (Week 3)

**Why SQLite?** It's a single-file, zero-setup database — no server to install or run, just a file called `tasks.db` that's created automatically the first time the app starts. Perfect for a small project like this, and a natural stepping stone before a "real" server-based database like Postgres.

**Where the database lives:** `tasks.db`, created automatically on first run. It's git-ignored, so every fresh clone starts with an empty database that self-seeds 3 example tasks.

**Example query I ran in DB Browser:**
```sql
UPDATE tasks SET done = 1;
```
This marked every task as completed — confirmed instantly through `GET /tasks` with no server restart needed, since the API and DB Browser read the same file.

![DB Browser screenshot](./db-browser-screenshot.png)

## Notes

- Week 2: data was in-memory only — restarting the server reset all tasks. That was intentional, to show the limits of memory-based storage.
- Week 3: data now persists in SQLite (`tasks.db`) — restarting the server no longer loses data. Tested by creating tasks, restarting, and confirming they're still present via both the API and DB Browser.

## Database (Week 1 · A3 — Postgres in Docker)

**Why Postgres + Docker?** SQLite was a single file — fine for small local projects, but real backends (including FlyRank's) run PostgreSQL as its own server. Docker lets you run that server without installing or configuring Postgres directly on your machine — the exact same container works identically on any computer.

**How to run the whole stack:**
```bash
cp .env.example .env
docker compose up
```
This starts both the API and the Postgres database together. On first run, the `tasks` table is created and seeded automatically.

**Environment variables** (see `.env.example`): `DATABASE_URL` — the connection string the app uses to reach Postgres.

**Example query:**
```sql
SELECT * FROM tasks;
```
Returns all seeded and created tasks, confirmed live in psql.

![Postgres data via psql](./postgres-screenshot.png)

## Notes (updated)

- Week 2: in-memory storage, lost on restart.
- Week 3 (A2): SQLite file, survives restarts, single file on disk.
- Week 1 (A3): PostgreSQL running in Docker, survives full container restarts thanks to a named volume (`taskdata`). Tested by creating a task, running `docker compose down` (removes containers) and `docker compose up` again — task was still present.