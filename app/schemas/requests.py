import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, condecimal
from app.models.model import Role


class BaseRequest(BaseModel):
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str

class UserForgotPasswordRequest(BaseRequest):
    username: str


class UserUpdateProfileRequest(BaseRequest):
    nik: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[str]
    phone_no: Optional[str]


class UserCreateRequest(BaseRequest):
    username: EmailStr
    password: str
    nik:str
    phone_no:str
    #role: Role = Role.merchant


class DeviceCreateRequest(BaseRequest):
    name: str
    serial_num: Optional[str]
    description: Optional[str]


class DeviceAssignRequest(BaseRequest):
    lat: float
    lon: float
    # serial_num: str
    # description: Optional[str]


class InvoiceBaseRequest(BaseRequest):
    invoice_num: str
    invoice_date: datetime.datetime
    device_name: str
    username: str
    tax_value: condecimal(max_digits=15, decimal_places=2)
    total_value: condecimal(max_digits=15, decimal_places=2)
