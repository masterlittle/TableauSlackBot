from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    BOT_NAME: str

    SLACK_SIGNING_SECRET: str
    SLACK_BOT_TOKEN: str

    SENTRY_DSN: Optional[str]
    LOGGING_LEVEL: str = "INFO"

    REDASH_API_KEY: Optional[str]
    REDASH_SERVER_URL: Optional[str]
    REDASH_WAIT_FOR_LOAD_TIME: int = 10

    TABLEAU_SERVER_URL: Optional[str]
    TABLEAU_PERSONAL_ACCESS_TOKEN_NAME: Optional[str]
    TABLEAU_PERSONAL_ACCESS_TOKEN_SECRET: Optional[str]
    TABLEAU_CONTENT_URL: Optional[str] = ""
    TABLEAU_SERVER_API_VERSION: Optional[str] = "3.10"
    TABLEAU_SERVER_IMAGE_API_TIMEOUT: int = 240

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    DATABASE_URI: Optional[PostgresDsn] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            port=values.get("POSTGRES_PORT"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"
