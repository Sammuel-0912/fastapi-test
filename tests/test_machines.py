async def test_read_machines_empty(client):
    response = await client.get("/machines/")
    assert response.status_code == 200
    assert response.json() == []  # 預期剛開始應該是空陣列


async def test_create_machine_without_token(client):
    """測試在『沒有攜帶 Token』的情況下新增機台，是否會被正確攔截 (401 或 412)"""
    payload = {"name": "CNC-001", "status": "operational", "location": "Line A"}
    response = await client.post("/machines/", json=payload)

    # 因為沒有token, 應該要被安全機制拒絕
    assert response.status_code in [401, 412]


async def test_full_auth_and_create_machine_flow(client):
    """測試完整流程：註冊 -> 登入取得 Token -> 成功建立機台"""

    # 1.註冊新帳號
    auth_payload = {"username": "testuser", "password": "testpassword"}
    reg_response = await client.post("/auth/register", json=auth_payload)
    assert reg_response.status_code == 201

    # 2.登入並取得Token(注意：OAuth2 表單格式要用 data= 而不是 json=)
    login_response = await client.post("/auth/login", data=auth_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3.攜帶Token挑戰新增機台
    machine_payload = {"name": "CNC-001", "status": "operational", "location": "Line B"}
    headers = {"Authorization": f"Bearer {token}"}  # 模擬前端 Headers 帶入 Token

    create_response = await client.post(
        "/machines/", json=machine_payload, headers=headers
    )

    # 4.驗證結果
    assert create_response.status_code == 201
    created_data = create_response.json()
    assert created_data["name"] == "CNC-001"
    assert created_data["location"] == "Line B"
    assert "id" in created_data
