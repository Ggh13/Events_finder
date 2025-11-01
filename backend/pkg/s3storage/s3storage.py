from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

class S3Config(BaseSettings):
    endpoint: str = Field(..., env="S3_ENDPOINT")
    access_key: str = Field(..., env="S3_ACCESS_KEY")
    secret_key: str = Field(..., env="S3_SECRET_KEY")
    bucket: str = Field(..., env="S3_BUCKET")
    region: str = Field("us-east-1", env="S3_REGION")
    secure: bool = Field(True, env="S3_SECURE")
