"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Database setup
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from databases import Database

DATABASE_URL = "sqlite+aiosqlite:///./activities.db"
database = Database(DATABASE_URL)
Base = declarative_base()

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    participants = relationship("Participant", back_populates="activity")

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", back_populates="participants")

# Create tables if not exist
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.get_event_loop().run_until_complete(create_tables())



@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")



import sqlalchemy as sa
from fastapi import Depends

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/activities")
async def get_activities():
    query = sa.select(Activity)
    rows = await database.fetch_all(query)
    result = {}
    for row in rows:
        # Get participants for each activity
        p_query = sa.select(Participant.email).where(Participant.activity_id == row.id)
        participants = [p[0] for p in await database.fetch_all(p_query)]
        result[row.name] = {
            "description": row.description,
            "schedule": row.schedule,
            "max_participants": row.max_participants,
            "participants": participants
        }
    return result



@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(activity_name: str, email: str):
    # Find activity
    query = sa.select(Activity).where(Activity.name == activity_name)
    activity = await database.fetch_one(query)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    # Check if already signed up
    p_query = sa.select(Participant).where(
        (Participant.activity_id == activity.id) & (Participant.email == email)
    )
    existing = await database.fetch_one(p_query)
    if existing:
        raise HTTPException(status_code=400, detail="Student is already signed up")
    # Check max participants
    p_count_query = sa.select(sa.func.count()).select_from(Participant).where(Participant.activity_id == activity.id)
    count = await database.fetch_val(p_count_query)
    if count >= activity.max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")
    # Add participant
    ins = Participant.__table__.insert().values(email=email, activity_id=activity.id)
    await database.execute(ins)
    return {"message": f"Signed up {email} for {activity_name}"}



@app.delete("/activities/{activity_name}/unregister")
async def unregister_from_activity(activity_name: str, email: str):
    # Find activity
    query = sa.select(Activity).where(Activity.name == activity_name)
    activity = await database.fetch_one(query)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    # Find participant
    p_query = sa.select(Participant).where(
        (Participant.activity_id == activity.id) & (Participant.email == email)
    )
    participant = await database.fetch_one(p_query)
    if not participant:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    # Remove participant
    del_query = Participant.__table__.delete().where(
        (Participant.activity_id == activity.id) & (Participant.email == email)
    )
    await database.execute(del_query)
    return {"message": f"Unregistered {email} from {activity_name}"}
