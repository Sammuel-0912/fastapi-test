from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 定義變數名稱與型態（名稱必須與 .env 檔案中的 Key 完全一致，大小寫不限
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# 實例化設定物件，供全域使用
settings = Settings()
