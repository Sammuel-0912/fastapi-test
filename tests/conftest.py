import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app

# 1. 建立一個專屬於測試的記憶體資料庫（速度極快，且執行完自動消失）
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """每次執行單一測試函式前，自動建立全新的資料表；執行完後自動刪除"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture
# def db_session():
#     """獲取測試用的資料庫 Session"""
#     connection = engine.connect()
#     transaction = connection.begin()
#     session = TestingSessionLocal(bind=connection)

#     yield session

#     session.close()
#     transaction.rollback()
#     connection.close()


@pytest_asyncio.fixture
async def client():
    async def _get_test_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db

    transport = ASGITransport(app=app)
    # 👈 允許自動跟隨轉址
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# 🆕 2. 認證 Header Fixture：自動註冊、登入並回傳 Authorization Header
@pytest_asyncio.fixture
async def auth_headers(client):
    """專門為管理員測試提供的 auth header (role="admin")"""
    async with TestingSessionLocal() as session:
        from app.security import hash_password

        admin_user = models.User(
            username="admin_test",
            hash_password=hash_password("password123"),
            role="admin",  # 👈 由測試環境預設造出管理員
        )
        session.add(admin_user)
        await session.commit()

    # 登入取得 Token
    login_resp = await client.post(
        "/auth/login", data={"username": "admin_test", "password": "password123"}
    )

    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def override_background_session(monkeypatch):
    """讓背景任務 notify_maintenance 使用測試記憶體資料庫，而非正式的 factory.db"""
    from app.routers import logs

    monkeypatch.setattr(logs, "SessionLocal", TestingSessionLocal)


@pytest_asyncio.fixture
async def test_machine():
    """建立一台測試用機台並回傳，供背景任務等測試使用"""
    async with TestingSessionLocal() as session:
        machine = models.Machine(
            name="Test-Machine", status="operational", location="Line A"
        )
        session.add(machine)
        await session.commit()
        await session.refresh(machine)
        return machine
