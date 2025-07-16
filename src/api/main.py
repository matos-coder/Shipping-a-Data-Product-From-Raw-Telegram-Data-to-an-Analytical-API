# src/api/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, schemas
from .database import get_db

app = FastAPI(
    title="Kara Solutions - Telegram Analytics API",
    description="An API to get insights from Ethiopian medical business Telegram channels.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Telegram Analytics API!"}

@app.get("/api/search/messages", response_model=List[schemas.Message])
def search_messages(query: str, db: Session = Depends(get_db)):
    """
    Searches for messages containing a specific keyword.
    Example: `/api/search/messages?query=paracetamol`
    """
    messages = crud.search_messages_by_keyword(db, keyword=query)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this keyword.")
    return messages

@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns the daily posting activity for a specific channel.
    Example: `/api/channels/Channel 123456789/activity`
    (Replace with a real channel name from your dim_channels table)
    """
    activity = crud.get_channel_activity(db, channel_name=channel_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Channel not found or no activity.")
    return activity

@app.get("/api/reports/top-visual-content", response_model=List[schemas.TopObject])
def get_top_visual_content(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns the most frequently detected objects in images across all channels.
    This helps answer: "Which channels have the most visual content (e.g., images of pills vs. creams)?"
    """
    top_objects = crud.get_top_detected_objects(db, limit=limit)
    return top_objects
