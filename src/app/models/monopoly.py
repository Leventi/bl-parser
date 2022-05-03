from pydantic import BaseModel


class BaseMonopoly(BaseModel):
    inn: str
    companyName: str
    registry: str
    section: str
    docNumber: str
    region: str
    address: str


class Monopoly(BaseMonopoly):
    id: int

    class Config:
        orm_mode = True
