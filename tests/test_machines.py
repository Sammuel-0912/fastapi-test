async def test_read_machines_empty(client):
    response = await client.get("/machines")
    assert response.status_code == 200
    assert response.json() == []  # 預期剛開始應該是空陣列


async def test_create_machine_without_token(client):
    """測試在『沒有攜帶 Token』的情況下新增機台，是否會被正確攔截 (401 或 412)"""
    payload = {"name": "CNC-001", "status": "operational", "location": "Line A"}
    response = await client.post("/machines", json=payload)

    # 修改後 (明確要求必須是 401 Unauthorized)
    assert response.status_code == 401


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
        "/machines", json=machine_payload, headers=headers
    )

    # 4.驗證結果
    assert create_response.status_code == 201
    created_data = create_response.json()
    assert created_data["name"] == "CNC-001"
    assert created_data["location"] == "Line B"
    assert "id" in created_data


async def test_delete_machine_success(client, auth_headers):
    # 1. 先建立一台測試用機台
    create_resp = await client.post(
        "/machines",
        json={"name": "Delete-Target-CNC", "location": "Line D"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    machine_id = create_resp.json()["id"]

    # 2. 發送 DELETE 請求刪除機台
    delete_resp = await client.delete(f"/machines/{machine_id}", headers=auth_headers)
    # 期望刪除成功（若為 HTTP 200 OK，驗證 status_code 與回傳訊息）
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Machine deleted successfully"

    # 3. 驗證再次查詢該機台時應回傳 404 Not Found
    get_resp = await client.get(f"/machines/{machine_id}")
    assert get_resp.status_code == 404


async def test_delete_machine_as_admin_success(client, auth_headers):
    """測試 admin 角色成功刪除機台"""
    # 1. 新增機台
    m_resp = await client.post(
        "/machines",
        json={"name": "Machine-To-Delete", "location": "Line A"},
        headers=auth_headers,
    )
    machine_id = m_resp.json()["id"]

    # 2. 刪除機台 (auth_headers 預設為 admin)
    delete_resp = await client.delete(f"/machines/{machine_id}", headers=auth_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Machine deleted successfully"


async def test_delete_machine_as_normal_user_forbidden(client):
    """測試一般 user 角色刪除機台被 403 阻擋"""
    # 1. 註冊一個普通 user 帳號 (role="user")
    user_payload = {
        "username": "normal_user",
        "password": "password123",
        "role": "user",
    }
    await client.post("/auth/register", json=user_payload)
    login_resp = await client.post("/auth/login", data=user_payload)
    user_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # 2. 嘗試刪除機台 (假設刪除 ID 1)
    del_resp = await client.delete("/machines/1", headers=user_headers)
    assert del_resp.status_code == 403
    assert del_resp.json()["detail"] == "權限不足，無法執行此操作"


async def test_delete_machine_without_token_unauthorized(client):
    """測試在『未攜帶 Token』的情況下刪除機台，應被阻擋並回傳 401"""
    response = await client.delete("/machines/1")
    assert response.status_code == 401
    # 完全未帶 token 時，是 OAuth2PasswordBearer 先擋下，回傳 FastAPI 預設訊息
    assert response.json()["detail"] == "Not authenticated"


async def test_register_role_injection_attack_fails(client):
    """測試攻擊者嘗試在註冊時注入 role="admin"，系統應忽視或阻止，建立出來的依然是普通 user"""
    attack_payload = {
        "username": "hacker",
        "password": "password123",
        "role": "admin",  # 💥 試圖提權攻擊
    }
    reg_resp = await client.post("/auth/register", json=attack_payload)
    assert reg_resp.status_code == 201

    # 驗證返回的使用者資訊，role 依然是被強制的 "user"
    user_data = reg_resp.json()
    assert user_data["role"] == "user"
