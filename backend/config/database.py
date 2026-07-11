from pydantic import BaseModel


class DbConfig(BaseModel):
    DB_ECHO: bool = False

    POSTGRES_USER: str = "sentra"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "sentra"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "db"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
