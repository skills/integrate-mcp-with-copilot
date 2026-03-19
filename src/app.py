"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


class ActivityPayload(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    schedule: str = Field(min_length=1)
    max_participants: int = Field(gt=0)


def validate_activity_payload(payload: ActivityPayload):
    cleaned_name = payload.name.strip()
    cleaned_description = payload.description.strip()
    cleaned_schedule = payload.schedule.strip()

    if not cleaned_name:
        raise HTTPException(status_code=400, detail="Activity name is required")

    if not cleaned_description:
        raise HTTPException(status_code=400, detail="Description is required")

    if not cleaned_schedule:
        raise HTTPException(status_code=400, detail="Schedule is required")

    return {
        "name": cleaned_name,
        "description": cleaned_description,
        "schedule": cleaned_schedule,
        "max_participants": payload.max_participants,
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities")
def create_activity(payload: ActivityPayload):
    activity_data = validate_activity_payload(payload)
    activity_name = activity_data["name"]

    if activity_name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    activities[activity_name] = {
        "description": activity_data["description"],
        "schedule": activity_data["schedule"],
        "max_participants": activity_data["max_participants"],
        "participants": [],
    }

    return {"message": f"Created activity {activity_name}"}


@app.put("/activities/{activity_name}")
def update_activity(activity_name: str, payload: ActivityPayload):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity_data = validate_activity_payload(payload)
    updated_name = activity_data["name"]
    existing_activity = activities[activity_name]
    participant_count = len(existing_activity["participants"])

    if activity_data["max_participants"] < participant_count:
        raise HTTPException(
            status_code=400,
            detail="Max participants cannot be lower than current enrollment",
        )

    if updated_name != activity_name and updated_name in activities:
        raise HTTPException(status_code=400, detail="Activity name already exists")

    updated_activity = {
        "description": activity_data["description"],
        "schedule": activity_data["schedule"],
        "max_participants": activity_data["max_participants"],
        "participants": existing_activity["participants"],
    }

    if updated_name != activity_name:
        del activities[activity_name]

    activities[updated_name] = updated_activity
    return {"message": f"Updated activity {updated_name}"}


@app.delete("/activities/{activity_name}")
def delete_activity(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    del activities[activity_name]
    return {"message": f"Deleted activity {activity_name}"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

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
