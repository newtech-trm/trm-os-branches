from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    username: str = Field(..., description="The user's unique username.")
    email: EmailStr = Field(..., description="The user's unique email address.")
    full_name: Optional[str] = Field(None, alias="fullName", description="The user's full name.")
    is_active: bool = Field(True, alias="isActive", description="Whether the user account is active.")
    
    model_config = ConfigDict(
        from_attributes=True, # Enable ORM mode for response serialization
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "fullName": "John Doe",
                "isActive": True
            }
        }
    )

class UserCreate(UserBase):
    password: str = Field(..., description="The user's password for account creation.")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, alias="fullName")
    is_active: Optional[bool] = Field(None, alias="isActive")

class UserInDB(UserBase):
    uid: str # This will be populated from the GraphModel's uid
    created_at: datetime
    updated_at: datetime

class User(UserInDB):
    pass
