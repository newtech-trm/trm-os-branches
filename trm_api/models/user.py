from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="The user's unique email address.")
    full_name: Optional[str] = Field(None, alias="fullName", description="The user's full name.")
    is_active: bool = Field(True, alias="isActive", description="Whether the user account is active.")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "fullName": "John Doe",
                "isActive": True
            }
        }
    )

class UserCreate(UserBase):
    # In a real system, you'd have password handling here.
    # For TRM-OS, a user might be created via an external auth provider.
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, alias="fullName")
    is_active: Optional[bool] = Field(None, alias="isActive")

class UserInDB(UserBase):
    user_id: str = Field(alias="userId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

class User(UserInDB):
    pass
