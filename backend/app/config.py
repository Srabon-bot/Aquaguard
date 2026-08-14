from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # protected_namespaces=() silences pydantic's warning about `model_path`
    # colliding with its reserved "model_" prefix -- a real field name here
    # (predates today's work), not a typo to rename.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=())

    cors_origins: str = "*"
    open_meteo_base_url: str = "https://api.open-meteo.com/v1/forecast"
    model_path: str = "app/models/artifacts/risk_model.joblib"  # old synthetic placeholder, kept for rollback
    flood_model_version: str = "2026-08-07c"  # backend/models/<version>/ -- see FloodGBMModel, DECISIONS.md SS19

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
