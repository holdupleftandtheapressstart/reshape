from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str

    # Local storage
    IMAGE_UPLOAD_DIR: str = "images"

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///./sql_app.db"

    class Config:
        case_sensitive = True


settings = Settings()
