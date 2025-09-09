from fastapi import FastAPI, Form, File, UploadFile, HTTPException, status
from db import events_collection
from pydantic import BaseModel
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader


cloudinary.config(
    cloud_name = "drgmfka1p",
    api_key = "554476864623376",
    api_secret = "s8E4i_dIariDrhs9E9-DIy_zAko"
)


tags_metadata = [
    {
        "name": "Home",
        "description": "Welcome to the event manager",
    },
    {
        "name": "Events",
        "description": "Events list",
    },
    {
        "name": "Updates",
        "description": "Updating and deleting"
    },
]

# Pydantic models
class EventModel(BaseModel):
    title: str
    description: str


app = FastAPI(openapi_tags=tags_metadata)

# Starting Endpoints 
@app.get("/", status_code=204, response_description="No Content", tags=["Home"])
def get_home():
    return {"message": "You are on the home page"}


# Events endpoints
@app.get("/events", tags=["Events"])
def get_events(title="", description="", limit=10, skip=0):
    # Get all events from database
    events = events_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}},
                {"description": {"$regex": description, "$options": "i"}},
            ]
        },
        limit=int(limit),
        skip=int(skip)
    ).to_list()
    # Return response
    return {"data": list(map(replace_mongo_id, events))}


@app.post("/events", tags=["Events"])
def post_event(
    title: Annotated[str, Form()], 
    description: Annotated[str, File()],
    flyer: Annotated[UploadFile, File()]):
   
    # Upload flyer to cloundinary to get a url
    upload_result = cloudinary.uploader.upload(flyer.file)
    # # Insert event into database
    events_collection.insert_one({
        "title": title,
        "description": description,
        "flyer_url": upload_result["secure_url"]
    })
    # events_collection.insert_one(event.model_dump())
    # # Return response
    return {"message": "Event added successfully"}


@app.get("/events/{event_id}", tags=["Events"])
def get_event_by_id(event_id):
    # Get event from database by id
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    return {"data": {"id": replace_mongo_id(event)}}

@app.put("/events/{event_id}", tags=["Update"])
def replace_event(
    event_id,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()]):
    # Check if event_id is valid mongo id
    # Upload flyer to cloudinary to get a url
    upload_result = cloudinary.uploader.upload(flyer.file)

    # Replace event in database
    events_collection.replace_one(
        filter={"id": ObjectId(event_id)},
        replacement={
            "title": title,
            "description": description,
            "flyer_url": upload_result["secure_url"],
        },
    )
    # Return response

    return {"message": "Event replaced successfully"}

@app.delete("/events/{event_id}", tags=["Update"])
def delete_events(event_id):
    # Check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!")
    
    # Delete event from database
    delete_result = events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No event found to delete")
    # Return response
    return {"message": "Event delete successfully!"}