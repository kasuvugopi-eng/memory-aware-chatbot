from pydantic import BaseModel
from typing import List
class memory(BaseModel):
    key:str
    value:str
class MemoryExtraction(BaseModel):
    memories:list[memory]    