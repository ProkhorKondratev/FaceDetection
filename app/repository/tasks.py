from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException

from app.db import get_db_session, TaskTable, ImageTable, FaceTable
from app.models import TaskModel, ImageModel, FaceModel


def get_task_repository(session: AsyncSession = Depends(get_db_session)) -> 'TaskRepository':
    return TaskRepository(session)


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_task(self) -> int:
        task = TaskTable()
        self._session.add(task)
        await self._session.commit()
        return task.id

    async def delete_task(self, task_id: int) -> None:
        task = await self._session.get(TaskTable, task_id)
        if not task:
            raise HTTPException(404, f"Задачи с ID {task_id} не существует")

        await self._session.delete(task)
        await self._session.commit()

    async def add_image(self, task_id: int, image_name: str, image_path: str):
        image = ImageTable(task_id=task_id, name=image_name, path=image_path)
        self._session.add(image)
        await self._session.commit()
        return image

    async def add_faces(self, image_id: int, faces_data: dict):
        faces = [
            FaceTable(
                image_id=image_id,
                bounding_box=face_data['bbox'],
                gender=face_data['demographics']['gender'],
                age=face_data['demographics']['age']['mean'],
            )
            for face_data in faces_data
        ]

        self._session.add_all(faces)
        await self._session.commit()
        return faces

    async def get_task_info(self, task_id: int) -> TaskModel:
        query = (
            select(TaskTable)
            .options(selectinload(TaskTable.images).selectinload(ImageTable.faces))
            .where(TaskTable.id == task_id)
        )
        result = await self._session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(404, f"Задачи с ID {task_id} не существует")

        total_faces = 0
        total_males = 0
        total_females = 0
        male_ages = []
        female_ages = []

        images_data = []
        for image in task.images:
            faces_data = []
            for face in image.faces:
                faces_data.append(FaceModel(bounding_box=face.bounding_box, gender=face.gender, age=face.age))
                total_faces += 1
                if face.gender == 'male':
                    total_males += 1
                    male_ages.append(face.age)
                elif face.gender == 'female':
                    total_females += 1
                    female_ages.append(face.age)
            images_data.append(ImageModel(name=image.name, faces=faces_data))

        average_male_age = round(sum(male_ages) / len(male_ages)) if male_ages else None
        average_female_age = round(sum(female_ages) / len(female_ages)) if female_ages else None

        task_model = TaskModel(
            id=task.id,
            images=images_data,
            total_faces=total_faces,
            total_males=total_males,
            total_females=total_females,
            average_male_age=average_male_age,
            average_female_age=average_female_age,
        )

        return task_model
