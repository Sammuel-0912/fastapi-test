from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="使用者名稱")
    password: str = Field(..., min_length=8, description="密碼至少要8碼")
    # 🆕 可選角色，預設為 "admin" (亦可改為 "user")


class UserResponse(BaseModel):
    id: int
    username: str
    role: str  # 🆕 回傳資料加上 role
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
