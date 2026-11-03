from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    genius_access_token: str = ""
    database_url: str = "postgresql+psycopg://Goatantix:Goatantix@localhost:5432/Goatantix"
    cors_origins: str = "http://localhost:5173"
    admin_password: str = "mdp"

    data_dir: Path = BACKEND_DIR / "data"

    @property
    def raw_dir(self) -> Path:
        d = self.data_dir / "raw"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def models_dir(self) -> Path:
        d = self.data_dir / "models"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
