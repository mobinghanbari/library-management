from pydantic import BaseModel


class OuIp(BaseModel):
    user_id: int
    ip_address: str
