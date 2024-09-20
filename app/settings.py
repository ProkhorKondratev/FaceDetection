from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FACECLOUD_API_URL: str
    FACECLOUD_API_EMAIL: str
    FACECLOUD_API_PASSWORD: str

    DB_NAME: str = 'facecloud'
    DB_USERNAME: str = 'facecloud'
    DB_PASSWORD: str = 'facecloud'
    DB_HOST: str = 'db'

    class Config:
        env_file = ".env"

    @property
    def DB_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}'


settings = Settings()
