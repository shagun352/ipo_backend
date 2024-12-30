from pydantic import BaseModel, Field



class PANResponse(BaseModel):
    pan_number: str
    username: str

    class Config:
        orm_mode = True

class IPOStatusResponse(BaseModel):
    id: str
    offer_price: str
    applicant_name: str
    company_name: str
    shares_applied: str
    shares_allotted: str
    adjusted_amount: str
    refund_amount: str
    category: str


class IPOPayload(BaseModel):
    client_id:str
    pan:str
    # token:str

