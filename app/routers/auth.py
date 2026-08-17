# app/routers/auth.py
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# 🆕 確保有匯入 select 與 AsyncSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, security
from app.config import settings
from app.database import get_db
from app.models.users import User
from app.schemas import user as user_schemas

router = APIRouter(prefix="/auth", tags=["Authentication (認證系統)"])


def require_role(*allowed_roles: str):
    """
    角色權限檢查依賴工廠 (RBAC)
    用法: user = Depends(require_role("admin", "manager"))
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> models.User:
        # 🆕 直接讀取 current_user.role
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="權限不足，無法執行此操作",
            )
        return current_user

    return role_checker


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 檢查帳號是否重複
    # db_user = (
    #     db.query(models.User).filter(models.User.username == user.username).first()
    # )
    stmt = select(models.User).where(models.User.username == user.username)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(status_code=400, detail="Username already registerd")

    # 密碼加密保存
    new_user = models.User(
        username=user.username,
        hash_password=security.hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    # # 找尋使用者
    # user = (
    #     db.query(models.User).filter(models.User.username == form_data.username).first()
    # )
    # if not user or not security.verify_password(form_data.password, user.hash_password):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號密碼錯誤"
    #     )
    # access_token = security.create_access_token(data={"sub": user.username})
    # return {"access_token": access_token, "token_type": "bearer"}

    # 🆕 3. 改成非同步的 select 語法
    stmt = select(models.User).filter(models.User.username == form_data.username)
    result = await db.execute(stmt)  # 加上 await
    user = result.scalar_one_or_none()
    # 驗證密碼（注意：如果是 user.hash_password 或 user.hashed_password，欄位名稱要與你的 Model 一致喔！）
    if not user or not security.verify_password(form_data.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號或密碼錯誤"
        )

    # 核發 Token
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無效的憑證，請重新登入",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # user = db.query(models.User).filter(models.User.username == username).first()
    # if user is None:
    #     raise credentials_exception
    # return user  # 回傳當前登入的使用者物件
    # 🆕 將原本的 db.query 改為非同步的 select
    stmt = select(models.User).filter(models.User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=user_schemas.UserResponse)
async def read_me(current_user: User = Depends(get_current_user)):
    """取得當前已登入使用者的個人資訊 (包含 role)"""
    return current_user
