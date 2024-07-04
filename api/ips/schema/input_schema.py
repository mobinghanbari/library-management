from pydantic import BaseModel, validator, IPvAnyAddress


class InIp(BaseModel):
    user_id: int
    ip_address: str

    @validator('ip_address')
    def validate_ip_address(cls, v):
        try:
            # Validate if the given string is a valid IP address (IPv4 or IPv6)
            ip = IPvAnyAddress(v)
        except ValueError:
            raise ValueError('Invalid IP address format.')
        return str(ip)
