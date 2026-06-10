from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    xai_api_base_url: str = os.getenv("XAI_API_BASE_URL", "https://api.x.ai")
    backend_cors_origins: str = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
