from fastapi import Form, File, UploadFile, HTTPException, status, APIRouter, Depends
from db import events_collection
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles



# Create users router
events_router = APIRouter()


# Events endpoints
@events_router.get("/events", tags=["Events"])
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


@events_router.post("/events", dependencies=[Depends(has_roles(["host", "admin"]))], tags=["Events"])
def post_event(
    title: Annotated[str, Form()], 
    description: Annotated[str, File()],
    flyer: Annotated[UploadFile, File()],
    user_id: Annotated[str, Depends(is_authenticated)]
):
    # Ensure an event with a title and user_id combined does not exist
    event_count = events_collection.count_documents(filter={
        "$and": [
            {"title": title},
            {"owner": user_id}
        ]
    })
    if event_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event with {title} and {user_id} already exist!",
        )


    # Upload flyer to cloundinary to get a url
    upload_result = cloudinary.uploader.upload(flyer.file)
    # # Insert event into database
    events_collection.insert_one({
        "title": title,
        "description": description,
        "flyer_url": upload_result["secure_url"],
        "owner": user_id
    })
    # events_collection.insert_one(event.model_dump())
    # # Return response
    return {"message": "Event added successfully"}


@events_router.get("/events/{event_id}", tags=["Events"])
def get_event_by_id(event_id):
    # Get event from database by id
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    return {"data": {"id": replace_mongo_id(event)}}

@events_router.put("/events/{event_id}", tags=["Update"])
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

@events_router.delete("/events/{event_id}", tags=["Update"])
def delete_events(event_id, user_id: Annotated[str, Depends(is_authenticated)]):
    # Check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!")
    
    # Delete event from database
    delete_result = events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No event found to delete")
    # Return response
    return {"message": "Event delete successfully!"}