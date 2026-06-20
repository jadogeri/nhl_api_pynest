from pydantic import BaseModel, ConfigDict
from typing import Optional

class Team(BaseModel):
    """
    Input validation model. Marked location fields as optional 
    to handle missing JSON keys without crashing the engine.
    """
    name: str
    city: str
    state: Optional[str] = None     # 👈 Made optional to handle entries like Washington, D.C.
    conference: str
    division: str
    stadium: Optional[str] = None   # 👈 Made optional for extra safety with older records

class TeamCreate(Team):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    conference: Optional[str] = None
    division: Optional[str] = None
    stadium: Optional[str] = None

class TeamResponse(Team):
    id: int

    model_config = ConfigDict(from_attributes=True)
