from curses.ascii import isalnum
from datetime import datetime
from operator import le
from fastapi import Path
from pydantic import BaseModel, validator

#Need to add field level validations.
class GenerateCashFreePaymentLinkRequest(BaseModel):
    class LinkNotify(BaseModel):
        send_sms: bool

    class CustomerDetails(BaseModel):
        customer_phone: str
    
    customer_details: CustomerDetails
    link_notify: LinkNotify = LinkNotify(send_sms=True)
    link_id: str
    link_amount: float
    link_currency: str = "INR"
    link_purpose: str
    link_partial_payments: bool = False
    link_expiry_time: datetime
    link_auto_reminders: bool = True

class GenerateOtp(BaseModel):
    token: str = Path(...)
    mobile_no: int = Path(...)

    @validator('mobile_no')
    def phone_validator(cls, v):
        assert len(v)==10 and v.isnumeric(), "Not a valid phone number."