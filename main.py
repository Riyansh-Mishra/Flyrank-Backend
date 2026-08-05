from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))  # reads .env into environment variables
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



app = FastAPI(title="Task API", version="1.0")
security = HTTPBearer()

DATABASE_URL = os.environ["DATABASE_URL"]

def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    cur.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cur.fetchone()["count"]
    if count == 0:
        cur.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            [("Buy milk", False), ("Walk the dog", False), ("Finish assignment", True)]
        )
    conn.commit()
    cur.close()
    conn.close()

init_db()  # runs once when the app starts

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class SignupLogin(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        if user_response is None or user_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
        (task.title, False)
    )
    new_row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_row

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if update.title is not None and not update.title.strip():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="title cannot be empty")

    new_title = row["title"] if update.title is None else update.title
    new_done = row["done"] if update.done is None else update.done

    cur.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
        (new_title, new_done, task_id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return updated

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return

@app.get("/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE done) AS done FROM tasks")
    row = cur.fetchone()
    cur.close()
    conn.close()
    total = row["total"]
    done = row["done"]
    return {"total": total, "done": done, "open": total - done}
@app.post("/auth/signup", status_code=201)
def signup(payload: SignupLogin):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user": result.user}

@app.post("/auth/login")
def login(payload: SignupLogin):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token
    }

@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    supabase.auth.sign_out()
    return

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}

@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {user.email}"}