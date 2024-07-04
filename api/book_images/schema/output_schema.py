from pydantic import BaseModel


class OuBookImage(BaseModel):
    id: int
    book_id: int
    image_url: str
