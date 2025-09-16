from fastapi import FastAPI
import cloudinary
import os
from dotenv import load_dotenv
from routes.events import events_router
from routes.users import users_router

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
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
        "name": "Update",
        "description": "Updating and deleting",
    },
    {
        "name": "Users",
        "description": "User registeration and login",
    },
]


app = FastAPI(
    title="🗒️Event Manager Api",
    description="For event managing",
    openapi_tags=tags_metadata
    )

# Starting Endpoints 
@app.get("/", tags=["Home"])
def get_home():
    return {"message": "You are on the home page"}

# Include routers
app.include_router(events_router)
app.include_router(users_router)
