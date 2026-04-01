"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Extended with task scheduling, calendar navigation, planned/unplanned/unfulfilled
and working dashboard features.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date, timedelta
from pathlib import Path
import os
from typing import Optional, List, Dict

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
}

class ActivitySignup(BaseModel):
    email: EmailStr


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    date: Optional[str] = None  # format YYYY-MM-DD
    time: Optional[str] = None  # format HH:MM
    priority: int = Field(1, ge=1, le=5)
    status: str = Field("pending")
    type: str = Field("planned")
    group: Optional[str] = None


class Task(TaskBase):
    id: int


class ClassDetails(BaseModel):
    id: int
    name: str
    schedule: str
    classroom: str
    study_task_ids: List[int] = []


TASK_STATUSES = {"pending", "in_progress", "completed", "unfulfilled"}
TASK_TYPES = {"planned", "unplanned", "study"}

tasks: Dict[int, Task] = {}
next_task_id = 1
classes: Dict[int, ClassDetails] = {
    1: ClassDetails(id=1, name="Math 10A", schedule="Mon 4:00-5:30", classroom="B12", study_task_ids=[]),
    2: ClassDetails(id=2, name="Science Lab", schedule="Wed 4:00-5:30", classroom="C03", study_task_ids=[]),
}


def parse_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def task_duplicate(date: Optional[str], time: Optional[str], title: str) -> bool:
    for task in tasks.values():
        if task.date == date and task.time == time and task.title == title:
            return True
    return False


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, signup: ActivitySignup):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if signup.email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity["participants"].append(signup.email)
    return {"message": f"Signed up {signup.email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: EmailStr):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.get("/tasks")
def list_tasks(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
):
    filtered = list(tasks.values())
    if status:
        filtered = [t for t in filtered if t.status == status]
    if type:
        filtered = [t for t in filtered if t.type == type]
    if date:
        filtered = [t for t in filtered if t.date == date]
    return filtered


@app.post("/tasks", status_code=201)
def create_task(task: TaskBase):
    global next_task_id

    if task.status not in TASK_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    if task.type not in TASK_TYPES:
        raise HTTPException(status_code=400, detail="Invalid type")

    if task.date and task.time:
        try:
            parse_date(task.date)
            datetime.strptime(task.time, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD and time HH:MM")

    if task_duplicate(task.date, task.time, task.title):
        raise HTTPException(status_code=400, detail="Task with same title at same date/time already exists")

    task_id = next_task_id
    next_task_id += 1
    created = Task(id=task_id, **task.dict())
    tasks[task_id] = created

    # Link study tasks to class if necessary
    if task.type == "study" and task.group:
        for cls in classes.values():
            if cls.name == task.group:
                cls.study_task_ids.append(task_id)
                break

    return created


@app.get("/tasks/unplanned")
def get_unplanned_tasks():
    return [t for t in tasks.values() if t.type == "unplanned"]


@app.get("/tasks/unfulfilled")
def get_unfulfilled_tasks():
    return [t for t in tasks.values() if t.status == "unfulfilled"]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskBase):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.status not in TASK_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    if payload.type not in TASK_TYPES:
        raise HTTPException(status_code=400, detail="Invalid type")

    if payload.date and payload.time:
        try:
            parse_date(payload.date)
            datetime.strptime(payload.time, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD and time HH:MM")

    if task_duplicate(payload.date, payload.time, payload.title) and not (
        tasks[task_id].date == payload.date
        and tasks[task_id].time == payload.time
        and tasks[task_id].title == payload.title
    ):
        raise HTTPException(status_code=400, detail="Task with same title at same date/time already exists")

    updated = tasks[task_id]
    updated.title = payload.title
    updated.description = payload.description
    updated.date = payload.date
    updated.time = payload.time
    updated.priority = payload.priority
    updated.status = payload.status
    updated.type = payload.type
    updated.group = payload.group

    tasks[task_id] = updated
    return updated


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    for cls in classes.values():
        if task_id in cls.study_task_ids:
            cls.study_task_ids.remove(task_id)
    return {"message": "Task deleted"}


@app.get("/calendar/month")
def month_view(year: int = Query(date.today().year), month: int = Query(date.today().month)):
    try:
        start = date(year, month, 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid year/month")
    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    calendar_tasks = [t for t in tasks.values() if t.date and start <= parse_date(t.date) <= end]
    return {
        "year": year,
        "month": month,
        "first_day": start.isoformat(),
        "last_day": end.isoformat(),
        "tasks": calendar_tasks,
    }


@app.get("/calendar/week")
def week_view(start_date: str = Query(date.today().isoformat())):
    try:
        start = parse_date(start_date)
    except Exception:
        raise HTTPException(status_code=400, detail="start_date must be YYYY-MM-DD")

    days = [start + timedelta(days=i) for i in range(7)]
    week_tasks = [t for t in tasks.values() if t.date and parse_date(t.date) in days]
    return {
        "week_start": start.isoformat(),
        "week_end": (start + timedelta(days=6)).isoformat(),
        "tasks": week_tasks,
    }


@app.get("/dashboard/working")
def working_dashboard(group: Optional[str] = None):
    target = [t for t in tasks.values() if t.status in {"pending", "in_progress", "unfulfilled"}]
    if group:
        target = [t for t in target if t.group == group]

    return {
        "total_tasks": len(tasks),
        "active_tasks": len([t for t in target if t.status in {"pending", "in_progress"}]),
        "unfulfilled_tasks": len([t for t in target if t.status == "unfulfilled"]),
        "group": group,
        "group_names": list({c.name for c in classes.values()}),
    }


@app.get("/classes")
def list_classes():
    return list(classes.values())


@app.get("/classes/{class_id}")
def class_details(class_id: int):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found")
    cls = classes[class_id]
    study_tasks = [tasks[t_id] for t_id in cls.study_task_ids if t_id in tasks]
    return {"class": cls, "study_tasks": study_tasks}

