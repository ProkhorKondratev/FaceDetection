from pydantic import BaseModel
from typing import List, Optional


class FaceModel(BaseModel):
    bounding_box: dict
    gender: str
    age: float

    class Config:
        from_attributes = True


class ImageModel(BaseModel):
    name: str
    faces: List[FaceModel]


class TaskModel(BaseModel):
    id: int
    images: List[ImageModel]
    total_faces: int
    total_males: int
    total_females: int
    average_male_age: Optional[float]
    average_female_age: Optional[float]
