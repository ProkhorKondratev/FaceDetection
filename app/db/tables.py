import os

from sqlalchemy import event, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .engine import Base


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    images: Mapped[list['Image']] = relationship('Image', back_populates='task', cascade='all, delete')


class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    path: Mapped[str] = mapped_column(String)

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'))
    task: Mapped['Task'] = relationship('Task', back_populates='images')

    faces: Mapped[list['Face']] = relationship('Face', back_populates='image', cascade='all, delete')


@event.listens_for(Image, 'before_delete')
def delete_image_file(mapper, connection, target: Image):
    if os.path.exists(target.path):
        os.remove(target.path)


class Face(Base):
    __tablename__ = 'faces'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bounding_box: Mapped[dict] = mapped_column(JSON)
    gender: Mapped[str] = mapped_column(String)
    age: Mapped[float] = mapped_column(Float)

    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id'))
    image: Mapped['Image'] = relationship('Image', back_populates='faces')
