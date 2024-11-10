from pydantic import BaseModel, Field,constr
from typing import Optional


class AccountingStart(BaseModel):
    acctsessionid: str
    acctuniqueid: str
    username: Optional[str]
    nasipaddress: str
    calledstationid: Optional[str]
    callingstationid: Optional[str]
    framedipaddress: Optional[str]
    servicetype: Optional[str]
    framedprotocol: Optional[str]


class AccountingStop(BaseModel):
    acctsessionid: str
    acctuniqueid: str
    acctsessiontime: int
    acctinputoctets: Optional[int]
    acctoutputoctets: Optional[int]
    acctterminatecause: Optional[str]


# Pydantic models for request validation
class User(BaseModel):
    username: constr(min_length=1, max_length=64)
    attribute: str = "Cleartext-Password"
    op: str = ":="
    value: str


class MACAddress(BaseModel):
    mac: str