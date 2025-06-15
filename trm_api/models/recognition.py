from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class RecognitionBase(BaseModel):
    win_id: str = Field(..., alias="winId", description="The ID of the WIN being recognized.")
    granter_user_id: str = Field(..., alias="granterId", description="The ID of the user giving the recognition.")
    recipient_user_ids: List[str] = Field(..., alias="recipientIds", description="A list of user IDs receiving the recognition.")
    title: str = Field(..., description="The title of the recognition.")
    description: Optional[str] = Field(None, description="A description or message of recognition.")
    recognition_date: Optional[datetime] = Field(None, alias="recognitionDate", description="Date when the recognition was given")
    recognition_type: Optional[str] = Field("Gratitude", alias="recognitionType", description="The type of recognition, e.g., 'Gratitude', 'Impact', 'Innovation'.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "Outstanding Project Completion",
                "description": "Incredible effort on the v2.1 release. Your dedication made it a success!",
                "winId": "win_abc_123",
                "granterId": "user_id_of_manager",
                "recipientIds": ["user_id_of_dev1", "user_id_of_dev2"],
                "recognitionDate": "2025-06-15T00:00:00",
                "recognitionType": "Impact"
            }
        }
    )

class RecognitionCreate(RecognitionBase):
    pass

# Recognitions are generally immutable, so an update model is minimal.
class RecognitionUpdate(BaseModel):
     message: Optional[str] = Field(None, description="The updated recognition message.")

class RecognitionInDB(RecognitionBase):
    recognition_id: str = Field(alias="recognitionId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)

class Recognition(RecognitionInDB):
    pass
