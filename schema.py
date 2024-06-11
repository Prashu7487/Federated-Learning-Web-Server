from pydantic import BaseModel


class User(BaseModel):
    name: str
    data_path: str
    password: str

class Parameter(BaseModel):
    client_parameter: dict
    client_id: int