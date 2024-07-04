from typing import Optional

from pydantic import BaseModel


class OuCategory(BaseModel):
    id: int
    name: str
    description: str
    parent_id: Optional[int] = None
