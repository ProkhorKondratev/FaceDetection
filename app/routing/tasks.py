from fastapi.routing import APIRouter
from fastapi import Depends, UploadFile, File

from app.services import get_task_service, TaskService
from app.models import TaskModel

router = APIRouter()


@router.post('/tasks', description='Создать задачу')
async def create_task(service: TaskService = Depends(get_task_service)):
    return await service.create_task()


@router.delete('/tasks', description='Удалить задачу')
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    return await service.delete_task(task_id)


@router.get('/tasks/{task_id}', description='Получить информацию о задаче')
async def get_task_info(task_id: int, service: TaskService = Depends(get_task_service)) -> TaskModel:
    return await service.get_task_info(task_id)


@router.post('/tasks/images', description='Добавить изображение к задаче')
async def add_image_to_task(
    task_id: int,
    image_name: str,
    image: UploadFile = File(),
    service: TaskService = Depends(get_task_service),
) -> TaskModel:
    return await service.add_image(task_id, image, image_name)
