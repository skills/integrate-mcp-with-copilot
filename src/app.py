"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

class ActivityCreate(BaseModel):
    name: str
    description: str
    schedule: str
    location: str
    advisor_email: str
    max_participants: int = Field(gt=0)


class ActivityUpdate(BaseModel):
    advisor_email: Optional[str] = None
    max_participants: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


professors = [
    {"name": "Avery Morgan", "email": "avery.morgan@mergington.edu"},
    {"name": "Jordan Lee", "email": "jordan.lee@mergington.edu"},
    {"name": "Taylor Brooks", "email": "taylor.brooks@mergington.edu"},
]

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "location": "Room 12",
        "advisor": professors[0],
        "max_participants": 12,
        "is_active": True,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "location": "Computer Lab",
        "advisor": professors[1],
        "max_participants": 20,
        "is_active": True,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "location": "Gymnasium",
        "advisor": professors[2],
        "max_participants": 30,
        "is_active": True,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "location": "Soccer Field",
        "advisor": professors[0],
        "max_participants": 22,
        "is_active": True,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "location": "Gymnasium",
        "advisor": professors[1],
        "max_participants": 15,
        "is_active": True,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "location": "Art Studio",
        "advisor": professors[2],
        "max_participants": 15,
        "is_active": True,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "location": "Auditorium",
        "advisor": professors[0],
        "max_participants": 20,
        "is_active": True,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "location": "Room 18",
        "advisor": professors[1],
        "max_participants": 10,
        "is_active": True,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "location": "Room 21",
        "advisor": professors[2],
        "max_participants": 12,
        "is_active": True,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.get("/professors")
def get_professors():
    return professors


@app.post("/activities", status_code=201)
def create_activity(activity_data: ActivityCreate):
    name = activity_data.name.strip()
    if not name or any(not value.strip() for value in (
        activity_data.description,
        activity_data.schedule,
        activity_data.location,
    )):
        raise HTTPException(status_code=400, detail="Club details cannot be empty")

    if name in activities:
        raise HTTPException(status_code=409, detail="A club with this name already exists")

    advisor = next(
        (professor for professor in professors
         if professor["email"] == activity_data.advisor_email),
        None,
    )
    if advisor is None:
        raise HTTPException(status_code=400, detail="Professor not found")

    activities[name] = {
        "description": activity_data.description.strip(),
        "schedule": activity_data.schedule.strip(),
        "location": activity_data.location.strip(),
        "advisor": advisor,
        "max_participants": activity_data.max_participants,
        "is_active": True,
        "participants": [],
    }
    return {"message": f"Created club {name}", "name": name}


@app.patch("/activities/{activity_name}")
def update_activity(activity_name: str, update_data: ActivityUpdate):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    updates = update_data.model_dump(exclude_unset=True)

    advisor = None
    if "advisor_email" in updates:
        advisor = next(
            (professor for professor in professors
             if professor["email"] == updates["advisor_email"]),
            None,
        )
        if advisor is None:
            raise HTTPException(status_code=400, detail="Professor not found")

    max_participants = None
    if "max_participants" in updates:
        max_participants = updates["max_participants"]
        if max_participants is None or max_participants < len(activity["participants"]):
            raise HTTPException(
                status_code=400,
                detail="Capacity cannot be lower than current enrollment",
            )

    is_active = updates.get("is_active")
    if "is_active" in updates:
        if is_active is None:
            raise HTTPException(status_code=400, detail="Club status cannot be empty")

    if advisor is not None:
        activity["advisor"] = advisor
    if max_participants is not None:
        activity["max_participants"] = max_participants
    if "is_active" in updates:
        activity["is_active"] = is_active

    return activity


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    if not activity["is_active"]:
        raise HTTPException(status_code=400, detail="This club is inactive")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="This club is full")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
