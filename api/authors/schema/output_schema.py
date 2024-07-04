from pydantic import BaseModel


class OuAuthor(BaseModel):
    id: int
    full_name: str
    nationality: str
