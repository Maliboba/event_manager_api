from dependencies.authn import authenticated_user
from fastapi import Depends, HTTPException, status
from typing import Annotated


permissions = [
    {
        "role": "admin",
        "permissions": [
            "post_event", 
            "get_events", 
            "get_event", 
            "put_event", 
            "delete_event", 
            "delete_user", 
            "put_user"]
    },
    {
         "role": "vendor",
        "permissions": [
            "post_event", 
            "get_events", 
            "get_event", 
            "put_event", 
            "delete_event"]
    },
    {
         "role": "guest",
        "permissions": [
            "get_events", 
            "get_event"]
    },
]


    



def has_roles(roles):
    def check_roles(user: Annotated[any, Depends(authenticated_user)]):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied!",
            )

    return check_roles

            
        