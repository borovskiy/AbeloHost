from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseModelSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseIdSchemaMixin:
    id: int


class BaseCreatedAndUpdateSchemaMixin:
    created_at: datetime
    updated_at: datetime
