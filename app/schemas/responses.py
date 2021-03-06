import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr, condecimal
from app.models.model import Role, Status


class BaseResponse(BaseModel):
    pass


class AccessTokenResponse(BaseResponse):
    token_type: str
    access_token: str
    exp: int
    iat: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int


class UserResponse(BaseResponse):
    id: uuid.UUID
    username: EmailStr
    verified:Optional[bool]
    nik: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[str]
    phone_no: Optional[str]
    role: Role

class UserConfirmationResponse(BaseResponse):
    id: uuid.UUID
    username: EmailStr
    verified:bool


class BaseUserResponse(BaseResponse):
    id: uuid.UUID
    username: EmailStr
    role: Role
    verified: bool
    nik:str
    phone_no:str


class UserDeviceResponse(BaseResponse):
    user_id: Optional[uuid.UUID]
    username: Optional[str]


class DeviceCreatedResponse(BaseResponse):
    id: uuid.UUID
    name: str
    serial_num: str
    description: str
    lat: Optional[float]
    lon: Optional[float]
    status: Status
    # user_id:Optional[uuid.UUID]


class DeviceResponse(BaseResponse):
    id: uuid.UUID
    name: str
    status: Optional[Status]
    serial_num: str
    description: str
    lat: Optional[float]
    lon: Optional[float]
    owner: Optional[UserDeviceResponse] = None


class DeviceAssignResponse(BaseResponse):
    id: uuid.UUID
    name: str
    user_id: Optional[uuid.UUID]
    status: Status


class UserDeviceReadResponse(UserResponse):
    role: Role
    devices: List[DeviceCreatedResponse] = []


class UserDeviceInResponse(UserResponse):
    devices: List[DeviceCreatedResponse] = []


class InvoiceBaseResponse(BaseResponse):
    id: uuid.UUID
    device_name: str
    username: str
    invoice_num: str
    invoice_date: datetime.datetime
    tax_value: condecimal(max_digits=15, decimal_places=2)
    total_value: condecimal(max_digits=15, decimal_places=2)

class InvoiceResponse(BaseResponse):
    device_name:str
    invoice_num: str
    invoice_date: datetime.datetime
    tax_value: condecimal(max_digits=15, decimal_places=2)
    total_value: condecimal(max_digits=15, decimal_places=2)


class DailyResponse(BaseResponse):
    username:str
    total: condecimal(max_digits=15, decimal_places=2)
    tax: condecimal(max_digits=15, decimal_places=2)
    count: int
    invoices: List[InvoiceResponse]
