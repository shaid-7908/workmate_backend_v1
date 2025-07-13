from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from bson import ObjectId
from typing import ClassVar

class UserSchema(BaseModel):
    user_name: str = Field(..., unique=True)
    user_email: str
    user_first_name: str
    user_last_name: str
    user_profile_picture: str | None = None
    user_password: str
    refresh_token: str = ""
    verified_status: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Collection name (like Mongoose model name)
    __collection_name__: ClassVar[str] = "users"

    model_config: ClassVar[ConfigDict] = {
        "title": "UserSchema",
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    } 