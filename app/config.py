from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 定義變數名稱與型態（名稱必須與 .env 檔案中的 Key 完全一致，大小寫不限
    secret_key: str = Field(..., min_length=1)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 🆕 新增 CORS 白名單設定，支援 List[str] 或由 JSON 字串解析
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# 實例化設定物件，供全域使用
settings = Settings()
