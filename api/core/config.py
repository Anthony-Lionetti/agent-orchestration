from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RabbitMQ Practice API"
    VERSION: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from environment

settings = Settings() 