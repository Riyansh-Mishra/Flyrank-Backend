# Task API

A simple CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with FastAPI. Data is stored in memory (no database) — it resets when the server restarts.

## How to run

1. Clone this repo and enter the folder:
```bash
   git https://github.com/Riyansh-Mishra/Flyrank-Backend.git
   cd Flyrank-Backend
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

## Example request

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

All endpoints listed and documented at `/docs`:

![Swagger UI endpoint list](./swagger-screenshot.png)

Testing a request live via "Try it out":

![Swagger UI request test](./swagger-request-screenshot.png)
