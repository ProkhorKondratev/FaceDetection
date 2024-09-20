import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .db import create_tables, drop_tables
from .routing import tasks_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logging.getLogger('watchfiles').setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Приложение запускается')
    await create_tables()
    yield
    # await drop_tables()
    logger.info('Приложение завершает работу')


app = FastAPI(lifespan=lifespan, title='Tevian FaceCloud', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    logger.info('Переадресация на /docs')
    return RedirectResponse(url='/docs')


@app.get('/health', include_in_schema=False)
async def health():
    return {'status': 'ok'}
