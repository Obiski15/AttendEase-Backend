from typing import Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: Optional[str] = None


class ItemInDBBase(ItemBase):
    id: int

    model_config = {"from_attributes": True}


class Item(ItemInDBBase):
    pass
