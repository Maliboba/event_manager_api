from fastapi import APIRouter, Form, HTTPException, status
from typing import Annotated
from pydantic import EmailStr
from db import users_collection
import bcrypt
import jwt
import os



# create users router
users_router = APIRouter()

# Define endpoints
@users_router.post("/users/register", tags=["Users"])
def register_user(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    ):

    # Ensure user does not exist
    user_count = users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exist!")
    
    # Hash user password 
    hashed_password = bcrypt.hashpw(bytes(password.encode("utf-8")), bcrypt.gensalt())
    

    #  Save user into database
    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password.decode("utf-8")
    })

   
    # Return response
    return {"message": "User registered successfully!"}


# Getting end point for login
@users_router.post("/users/login", tags=["Users"])
def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)]
):

    # Ensure user exist
    user = users_collection.find_one({"email": email})
    if not user :
        raise HTTPException(status.HTTP_404_NOT_FOUND,"User does not exist!")
    
    # Retrieve the hashed password from the database
    hashed_password_in_db = user["password"]
    correct_password = bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password_in_db.encode("utf-8")
    )

    if not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Generate for them an access token
    encoded_jwt = jwt.encode({"id": str(user["_id"])}, os.getenv("JWT_SECRET_KEY"), "HS256")

    return {
        "message": "User logged in successfully!",
        "access_token": encoded_jwt
        }

