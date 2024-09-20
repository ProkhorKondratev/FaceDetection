from fastapi import Depends, UploadFile, status
from fastapi.responses import JSONResponse

from app.adapters import Uploader, FaceCloud, get_uploader, get_facecloud
from app.repository import TaskRepository, get_task_repository
from app.models import TaskModel


def get_task_service(
    uploader: Uploader = Depends(get_uploader),
    facecloud: FaceCloud = Depends(get_facecloud),
    repository: TaskRepository = Depends(get_task_repository),
) -> 'TaskService':
    return TaskService(uploader, facecloud, repository)


class TaskService:
    def __init__(self, uploader: Uploader, facecloud: FaceCloud, repository: TaskRepository):
        self._uploader = uploader
        self._facecloud = facecloud
        self._repository = repository

    async def create_task(self) -> JSONResponse:
        task_id = await self._repository.create_task()
        return JSONResponse({'task_id': task_id}, status_code=status.HTTP_201_CREATED)

    async def delete_task(self, id: int) -> JSONResponse:
        await self._repository.delete_task(id)
        return JSONResponse('Задача успешно удалена', status_code=status.HTTP_200_OK)

    async def add_image(self, task_id: int, image: UploadFile, image_name: str | None) -> TaskModel:
        image_path = await self._uploader.upload_image(image)
        image_name = image_name or image_path.stem

        image_obj = await self._repository.add_image(task_id, image_name, str(image_path))
        faces_data = await self._facecloud.detect_faces(image_path)
        await self._repository.add_faces(image_obj.id, faces_data)

        return await self._repository.get_task_info(task_id)

    async def get_task_info(self, task_id: int) -> TaskModel:
        return await self._repository.get_task_info(task_id)
